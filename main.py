"""
Main entry point for Annual Report Analyzer MVP.
Provides CLI interface and application startup.
"""

import asyncio
import sys
import os
from pathlib import Path
import argparse
from typing import Optional

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.utils.config import get_config, load_environment_file
from src.utils.logging_config import setup_logging, get_logger
from src.orchestrator.mvp_orchestrator import MVPOrchestrator


def setup_environment():
    """Setup environment and configuration."""
    # Load environment variables
    load_environment_file()
    
    # Get configuration
    config = get_config()
    
    # Setup logging
    setup_logging(
        level="INFO",
        log_file="./logs/main.log",
        format_type="console"
    )
    
    # Validate configuration
    if not config.validate_azure_config():
        print("\n❌ Azure OpenAI configuration is invalid!")
        print("Please check your .env file and ensure these variables are set:")
        print("  - AZURE_OPENAI_ENDPOINT")
        print("  - AZURE_OPENAI_API_KEY") 
        print("  - AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        print("  - AZURE_OPENAI_CHAT_DEPLOYMENT")
        print("\nYou can copy .env.example to .env and update the values.")
        return None
    
    # Setup directories
    config.setup_directories()
    
    return config


async def run_interactive_mode():
    """Run in interactive CLI mode."""
    logger = get_logger("main")
    
    print("\n🚀 Annual Report Analyzer MVP - Interactive Mode")
    print("=" * 50)
    
    # Initialize orchestrator
    print("Initializing components...")
    orchestrator = MVPOrchestrator()
    
    # Health check
    print("Performing health check...")
    health = await orchestrator.health_check()
    
    if health["overall_status"] != "healthy":
        print(f"⚠️  System health: {health['overall_status']}")
        for component, status in health["components"].items():
            status_emoji = "✅" if status.get("status") == "healthy" else "❌"
            print(f"  {status_emoji} {component}: {status.get('status', 'unknown')}")
    else:
        print("✅ All components are healthy!")
    
    print("\nCommands:")
    print("  upload <path>  - Process a PDF document")
    print("  query <text>   - Ask a question about processed documents")
    print("  list           - List processed documents")
    print("  stats          - Show system statistics")
    print("  health         - Check system health")
    print("  quit           - Exit the application")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input:
                continue
            
            parts = user_input.split(None, 1)
            command = parts[0].lower()
            
            if command == "quit":
                print("Goodbye! 👋")
                break
            
            elif command == "upload":
                if len(parts) < 2:
                    print("Usage: upload <pdf_path>")
                    continue
                
                pdf_path = parts[1]
                if not os.path.exists(pdf_path):
                    print(f"File not found: {pdf_path}")
                    continue
                
                print(f"Processing document: {pdf_path}")
                try:
                    result = await orchestrator.process_document(pdf_path)
                    print(f"✅ Processed successfully!")
                    print(f"  📄 Document: {result['document_filename']}")
                    print(f"  📖 Pages: {result['total_pages']}")
                    print(f"  🧩 Chunks: {result['chunks_created']}")
                    print(f"  ⏱️  Time: {result['processing_time_seconds']:.1f}s")
                except Exception as e:
                    print(f"❌ Processing failed: {e}")
            
            elif command == "query":
                if len(parts) < 2:
                    print("Usage: query <your question>")
                    continue
                
                question = parts[1]
                print(f"Answering: {question}")
                
                try:
                    result = await orchestrator.query_document(question)
                    
                    if result["status"] == "no_results":
                        print("❌ No relevant information found")
                        print(f"💬 {result['answer']}")
                    else:
                        print(f"✅ Answer (confidence: {result['confidence']:.2f}):")
                        print(f"💬 {result['answer']}")
                        print(f"\n📚 Citations ({len(result['citations'])}):")
                        for cit in result['citations'][:3]:  # Show top 3
                            pages = ", ".join(map(str, cit['page_numbers']))
                            print(f"  • {cit['source_document']} (pages {pages})")
                            print(f"    {cit['text_preview'][:100]}...")
                
                except Exception as e:
                    print(f"❌ Query failed: {e}")
            
            elif command == "list":
                try:
                    docs = orchestrator.get_processed_documents()
                    if not docs:
                        print("No documents have been processed yet.")
                    else:
                        print("📚 Processed Documents:")
                        for doc in docs:
                            pages = f"{min(doc['pages'])}-{max(doc['pages'])}" if doc['pages'] else "0"
                            print(f"  • {doc['filename']}")
                            print(f"    📖 Pages: {pages} | 🧩 Chunks: {doc['chunks_count']}")
                except Exception as e:
                    print(f"❌ Failed to list documents: {e}")
            
            elif command == "stats":
                try:
                    stats = orchestrator.vector_store.get_stats()
                    docs = orchestrator.get_processed_documents()
                    
                    print("📊 System Statistics:")
                    print(f"  📄 Documents: {len(docs)}")
                    print(f"  🧩 Total chunks: {stats['total_vectors']}")
                    print(f"  📐 Embedding dimension: {stats['embedding_dimension']}")
                    print(f"  🔍 Index type: {stats['index_type']}")
                    print(f"  💾 Storage: {stats['persist_directory']}")
                except Exception as e:
                    print(f"❌ Failed to get stats: {e}")
            
            elif command == "health":
                try:
                    health = await orchestrator.health_check()
                    print(f"🩺 Overall Status: {health['overall_status']}")
                    for component, status in health["components"].items():
                        status_emoji = "✅" if status.get("status") == "healthy" else "❌"
                        print(f"  {status_emoji} {component}: {status.get('status', 'unknown')}")
                except Exception as e:
                    print(f"❌ Health check failed: {e}")
            
            else:
                print(f"Unknown command: {command}")
                print("Type 'quit' to exit or use one of the available commands.")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            logger.error(f"Unexpected error in interactive mode: {e}")
            print(f"❌ Unexpected error: {e}")


async def run_api_mode(host: str = None, port: int = None):
    """Run in API server mode."""
    import uvicorn
    from src.api.fastapi_app import app
    
    config = get_config()
    host = host or config.api.host
    port = port or config.api.port
    
    print(f"\n🚀 Starting Annual Report Analyzer API")
    print(f"📡 Server: http://{host}:{port}")
    print(f"📖 Documentation: http://{host}:{port}/docs")
    print(f"🔄 Interactive docs: http://{host}:{port}/redoc")
    print("=" * 50)
    
    uvicorn.run(
        "src.api.fastapi_app:app",
        host=host,
        port=port,
        reload=config.api.debug,
        log_level="info"
    )


def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(
        description="Annual Report Analyzer MVP",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Interactive mode
  python main.py --api             # API server mode  
  python main.py --api --port 8080 # API server on custom port
  python main.py --process document.pdf --query "What was the revenue?"
        """
    )
    
    parser.add_argument(
        "--api", 
        action="store_true",
        help="Run as API server"
    )
    
    parser.add_argument(
        "--host",
        default=None,
        help="API server host (default: from config)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=None,
        help="API server port (default: from config)"
    )
    
    parser.add_argument(
        "--process",
        help="Process a specific PDF document"
    )
    
    parser.add_argument(
        "--query",
        help="Query processed documents (use with --process or existing docs)"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true", 
        help="Run in interactive CLI mode (default)"
    )
    
    args = parser.parse_args()
    
    # Setup environment
    config = setup_environment()
    if config is None:
        sys.exit(1)
    
    # Determine mode
    if args.api:
        # API server mode
        asyncio.run(run_api_mode(args.host, args.port))
    
    elif args.process or args.query:
        # Single operation mode
        async def single_operation():
            orchestrator = MVPOrchestrator()
            
            if args.process:
                print(f"Processing document: {args.process}")
                result = await orchestrator.process_document(args.process)
                print(f"Processed: {result['chunks_created']} chunks in {result['processing_time_seconds']:.1f}s")
            
            if args.query:
                print(f"Query: {args.query}")
                result = await orchestrator.query_document(args.query)
                print(f"Answer: {result['answer']}")
                print(f"Confidence: {result['confidence']:.2f}")
        
        asyncio.run(single_operation())
    
    else:
        # Interactive mode (default)
        asyncio.run(run_interactive_mode())


if __name__ == "__main__":
    main()
