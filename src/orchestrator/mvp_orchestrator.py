"""
MVP Orchestrator for Annual Report Analyzer.
Coordinates document processing, embedding generation, and query processing.
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

from src.azure.embedding_client import AzureEmbeddingClient
from src.azure.chat_client import AzureChatClient
from src.extractors.text_extractor import TextExtractor, Document
from src.rag.chunking_strategy import BasicChunkingStrategy, Chunk
from src.rag.vector_store import ChromaVectorStore
from src.utils.config import get_config
from src.utils.logging_config import get_logger, LoggerMixin, log_performance, log_error


class MVPOrchestrator(LoggerMixin):
    """
    Main orchestrator for MVP functionality.
    Handles end-to-end document processing and query answering.
    """
    
    def __init__(self, config_override: Optional[Dict] = None):
        """
        Initialize MVP orchestrator with all required components.
        
        Args:
            config_override: Optional configuration overrides
        """
        self.config = get_config()
        if config_override:
            # Apply any configuration overrides
            for key, value in config_override.items():
                setattr(self.config, key, value)
        
        # Initialize components
        self._initialize_components()
        
        # Processing state
        self.processed_documents: Dict[str, str] = {}  # filename -> document_id mapping
        self.current_document: Optional[Document] = None
        
        self.logger.info("MVP Orchestrator initialized successfully")
    
    def _initialize_components(self):
        """Initialize all required components."""
        try:
            # Text extraction
            self.text_extractor = TextExtractor(
                max_file_size_mb=50
            )
            
            # Chunking strategy
            self.chunker = BasicChunkingStrategy(
                chunk_size=self.config.rag.chunk_size,
                chunk_overlap=self.config.rag.chunk_overlap,
                preserve_financial_tables=True
            )
            
            # Azure OpenAI clients
            self.embedding_client = AzureEmbeddingClient(
                endpoint=self.config.azure_openai.endpoint,
                api_key=self.config.azure_openai.api_key,
                deployment_name=self.config.azure_openai.embedding_deployment,
                api_version=self.config.azure_openai.api_version,
                max_concurrent_requests=5
            )
            
            self.chat_client = AzureChatClient(
                endpoint=self.config.azure_openai.endpoint,
                api_key=self.config.azure_openai.api_key,
                deployment_name=self.config.azure_openai.chat_deployment,
                api_version=self.config.azure_openai.api_version,
                max_tokens=self.config.azure_openai.max_tokens,
                temperature=self.config.azure_openai.temperature
            )
            
            # Vector store
            self.vector_store = ChromaVectorStore(
                persist_directory=self.config.rag.persist_directory
            )
            
            self.logger.info("All components initialized successfully")
            
        except Exception as e:
            self.logger.error("Failed to initialize components", **log_error(e))
            raise
    
    async def process_document(self, pdf_path: str) -> Dict[str, Any]:
        """
        Process a PDF document and build vector index.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Processing results dictionary
            
        Raises:
            Exception: If processing fails
        """
        start_time = time.time()
        
        try:
            self.logger.info(f"Starting document processing: {pdf_path}")
            
            # Step 1: Extract text from PDF
            self.logger.info("Extracting text from PDF...")
            document = self.text_extractor.extract_text_from_pdf(pdf_path)
            self.current_document = document
            
            # Step 2: Chunk the document
            self.logger.info("Chunking document...")
            chunks = self.chunker.chunk_document(document)
            
            if not chunks:
                raise ValueError("No valid chunks extracted from document")
            
            # Step 3: Generate embeddings
            self.logger.info(f"Generating embeddings for {len(chunks)} chunks...")
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = await self.embedding_client.get_embeddings(chunk_texts)
            
            # Step 4: Add to vector store
            self.logger.info("Adding chunks to vector store...")
            self.vector_store.add_documents(chunks, embeddings)
            
            # Vector store automatically persists in ChromaDB
            self.logger.info("Document successfully added to vector store")
            
            # Update processed documents registry
            self.processed_documents[document.filename] = document.filename
            
            duration = time.time() - start_time
            
            processing_results = {
                "status": "success",
                "document_filename": document.filename,
                "total_pages": document.total_pages,
                "chunks_created": len(chunks),
                "embeddings_generated": len(embeddings),
                "processing_time_seconds": duration,
                "vector_store": "ChromaDB (auto-persisted)",
                "document_metadata": document.metadata
            }
            
            self.logger.info(
                "Document processing completed successfully",
                **log_performance(
                    "process_document",
                    duration,
                    filename=document.filename,
                    pages=document.total_pages,
                    chunks=len(chunks)
                )
            )
            
            return processing_results
            
        except Exception as e:
            self.logger.error(
                "Document processing failed",
                **log_error(e, {"pdf_path": pdf_path})
            )
            raise
    
    async def query_document(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Query the processed document and generate answer.
        
        Args:
            query: User's question
            top_k: Number of relevant chunks to retrieve
            
        Returns:
            Query results with answer and citations
            
        Raises:
            ValueError: If no document is processed
            Exception: If query processing fails
        """
        if self.vector_store.get_stats()["total_vectors"] == 0:
            raise ValueError("No documents have been processed. Please process a document first.")
        
        start_time = time.time()
        
        try:
            self.logger.info(f"Processing query: {query[:100]}...")
            
            # Step 1: Generate query embedding
            self.logger.debug("Generating query embedding...")
            query_embedding = await self.embedding_client.get_embedding(query)
            
            # Step 2: Similarity search
            self.logger.debug("Performing similarity search...")
            search_results = self.vector_store.similarity_search(
                query_embedding,
                k=top_k,
                score_threshold=self.config.rag.score_threshold
            )
            
            if not search_results:
                return {
                    "status": "no_results",
                    "answer": "I couldn't find relevant information to answer your question. Please try rephrasing your query or ask about different aspects of the document.",
                    "citations": [],
                    "confidence": 0.0
                }
            
            # Step 3: Build context from search results
            self.logger.debug("Building context from search results...")
            context_builder_result = self._build_context(search_results, query)
            
            # Step 4: Generate answer using chat client
            self.logger.debug("Generating answer...")
            chat_response = await self.chat_client.generate_answer(
                context=context_builder_result["context"],
                query=query,
                include_citations=True
            )
            
            # Step 5: Build final response
            response = self._build_query_response(
                query=query,
                search_results=search_results,
                context_info=context_builder_result,
                chat_response=chat_response,
                processing_time=time.time() - start_time
            )
            
            self.logger.info(
                "Query processed successfully",
                **log_performance(
                    "query_document",
                    time.time() - start_time,
                    query_length=len(query),
                    results_found=len(search_results),
                    answer_length=len(chat_response.content)
                )
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Query processing failed",
                **log_error(e, {"query": query[:100]})
            )
            raise
    
    def _build_context(self, search_results: List, query: str) -> Dict[str, Any]:
        """
        Build context string from search results.
        
        Args:
            search_results: List of hit dictionaries from ChromaVectorStore
            query: Original query for context optimization
            
        Returns:
            Dictionary with context and metadata
        """
        context_parts = []
        citations = []
        total_chars = 0
        max_context_chars = 4000  # Leave room for query and system prompt
        
        for i, hit in enumerate(search_results):
            chunk_text = hit["document"]
            chunk_metadata = hit["metadata"]
            distance = hit["distance"]
            
            source_doc = chunk_metadata.get("source_document", "unknown")
            page_numbers_str = chunk_metadata.get("page_numbers", "1")
            
            # Parse page numbers back from string
            try:
                page_nums = [int(p.strip()) for p in page_numbers_str.split(",") if p.strip()]
            except (ValueError, AttributeError):
                page_nums = [1]
            
            # Check if adding this chunk would exceed limit
            if total_chars + len(chunk_text) > max_context_chars and context_parts:
                break
            
            # Add chunk with citation marker
            context_part = f"[Source {i+1}] {chunk_text}"
            context_parts.append(context_part)
            total_chars += len(context_part)
            
            # Build citation info
            # Convert distance to similarity score (1 - distance)
            similarity_score = 1.0 - distance
            
            citation = {
                "citation_id": i + 1,
                "source_document": source_doc,
                "page_numbers": page_nums,
                "relevance_score": float(similarity_score),
                "chunk_id": hit["id"],
                "text_preview": chunk_text[:150] + "..." if len(chunk_text) > 150 else chunk_text
            }
            citations.append(citation)
        
        context = "\n\n".join(context_parts)
        
        return {
            "context": context,
            "citations": citations,
            "chunks_used": len(context_parts),
            "total_chars": total_chars
        }
    
    def _build_query_response(
        self,
        query: str,
        search_results: List,
        context_info: Dict,
        chat_response,
        processing_time: float
    ) -> Dict[str, Any]:
        """
        Build comprehensive query response.
        
        Args:
            query: Original query
            search_results: Raw search results
            context_info: Context building results
            chat_response: Chat client response
            processing_time: Total processing time
            
        Returns:
            Complete query response dictionary
        """
        # Calculate confidence based on search scores and response quality
        # Convert distances to similarity scores and calculate average
        similarity_scores = [1.0 - hit["distance"] for hit in search_results]
        avg_score = sum(similarity_scores) / len(similarity_scores)
        confidence = min(avg_score * 1.2, 1.0)  # Boost confidence slightly, cap at 1.0
        
        # Determine if response seems complete
        response_quality = self._assess_response_quality(chat_response.content, query)
        
        return {
            "status": "success",
            "query": query,
            "answer": chat_response.content,
            "citations": context_info["citations"],
            "confidence": confidence,
            "metadata": {
                "chunks_retrieved": len(search_results),
                "chunks_used": context_info["chunks_used"],
                "processing_time_seconds": processing_time,
                "tokens_used": chat_response.usage,
                "context_length": context_info["total_chars"],
                "response_quality": response_quality,
                "model_used": chat_response.model
            }
        }
    
    def _assess_response_quality(self, answer: str, query: str) -> Dict[str, Any]:
        """
        Assess the quality of generated response.
        
        Args:
            answer: Generated answer
            query: Original query
            
        Returns:
            Quality assessment metrics
        """
        return {
            "answer_length": len(answer),
            "has_numbers": any(char.isdigit() for char in answer),
            "has_financial_terms": any(
                term in answer.lower() 
                for term in ["revenue", "profit", "margin", "growth", "expenses", "%", "$"]
            ),
            "seems_complete": len(answer) > 50 and answer.endswith((".", "!", "?")),
            "addresses_query": any(
                word in answer.lower() 
                for word in query.lower().split() 
                if len(word) > 3
            )
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check of all components.
        
        Returns:
            Health check results
        """
        health_results = {
            "overall_status": "healthy",
            "components": {},
            "timestamp": time.time()
        }
        
        try:
            # Check embedding client
            embedding_health = await self.embedding_client.health_check()
            health_results["components"]["embedding_client"] = embedding_health
            
            # Check chat client
            chat_health = await self.chat_client.health_check()
            health_results["components"]["chat_client"] = chat_health
            
            # Check vector store
            vector_stats = self.vector_store.get_stats()
            health_results["components"]["vector_store"] = {
                "status": "healthy" if vector_stats["total_vectors"] >= 0 else "unhealthy",
                **vector_stats
            }
            
            # Check overall status
            component_statuses = [
                comp.get("status", "unknown") 
                for comp in health_results["components"].values()
            ]
            
            if any(status != "healthy" for status in component_statuses):
                health_results["overall_status"] = "degraded"
            
            return health_results
            
        except Exception as e:
            health_results["overall_status"] = "unhealthy"
            health_results["error"] = str(e)
            return health_results
    
    def get_processed_documents(self) -> List[Dict[str, Any]]:
        """
        Get list of processed documents.
        
        Returns:
            List of processed document information
        """
        try:
            # Get document info from vector store (this is the source of truth)
            documents_info = self.vector_store.get_documents_info()
            
            # Add processing timestamps - use current time as placeholder since 
            # ChromaDB doesn't store timestamps by default
            current_time = time.time()
            for doc_info in documents_info:
                filename = doc_info["filename"]
                # Always set a processing date for display purposes
                doc_info["processing_date"] = current_time
                
                # Also update our in-memory registry to stay in sync
                if filename not in self.processed_documents:
                    self.processed_documents[filename] = filename
            
            return documents_info
            
        except Exception as e:
            self.logger.error(f"Failed to get processed documents: {e}")
            return []


if __name__ == "__main__":
    # Test the orchestrator
    import asyncio
    import os
    
    async def test_orchestrator():
        # Load environment variables
        from src.utils.config import load_environment_file
        load_environment_file()
        
        # Create orchestrator
        orchestrator = MVPOrchestrator()
        
        # Test health check
        health = await orchestrator.health_check()
        print("Health check:")
        print(f"  Overall status: {health['overall_status']}")
        for component, status in health["components"].items():
            print(f"  {component}: {status.get('status', 'unknown')}")
        
        # Test with a document (if available)
        test_pdf = "data/sample_annual_report.pdf"
        if os.path.exists(test_pdf):
            print(f"\nProcessing test document: {test_pdf}")
            result = await orchestrator.process_document(test_pdf)
            print(f"Processing result: {result['status']}")
            print(f"Chunks created: {result['chunks_created']}")
            
            # Test query
            query = "What was the total revenue mentioned in the document?"
            print(f"\nQuerying: {query}")
            answer = await orchestrator.query_document(query)
            print(f"Answer: {answer['answer'][:200]}...")
            print(f"Confidence: {answer['confidence']:.2f}")
            print(f"Citations: {len(answer['citations'])}")
        else:
            print(f"Test document not found: {test_pdf}")
    
    # Run test if configuration is valid
    config = get_config()
    if config.validate_azure_config():
        asyncio.run(test_orchestrator())
    else:
        print("Please configure Azure OpenAI settings in .env file")
