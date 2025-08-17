"""
FastAPI application for Annual Report Analyzer MVP.
Provides REST API endpoints for document processing and querying.
"""

import asyncio
import os
import tempfile
from typing import Dict, List, Optional, Any
from pathlib import Path
import time

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

from src.orchestrator.mvp_orchestrator import MVPOrchestrator
from src.utils.config import get_config, load_environment_file
from src.utils.logging_config import setup_logging, get_logger


# Load environment variables and setup logging
load_environment_file()
config = get_config()
setup_logging(level="INFO", log_file="./logs/api.log")

# Create FastAPI app
app = FastAPI(
    title="Annual Report Analyzer API",
    description="MVP API for analyzing annual reports using RAG and Azure OpenAI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global logger
logger = get_logger("api")

# Global orchestrator instance
orchestrator: Optional[MVPOrchestrator] = None


# Request/Response models
class QueryRequest(BaseModel):
    """Request model for document queries."""
    question: str = Field(..., min_length=5, max_length=500, description="Question to ask about the document")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of relevant chunks to retrieve")


class Citation(BaseModel):
    """Citation information."""
    citation_id: int
    source_document: str
    page_numbers: List[int]
    relevance_score: float
    text_preview: str


class QueryResponse(BaseModel):
    """Response model for document queries."""
    status: str
    query: str
    answer: str
    citations: List[Citation]
    confidence: float
    metadata: Dict[str, Any]


class ProcessingResponse(BaseModel):
    """Response model for document processing."""
    status: str
    document_filename: str
    total_pages: int
    chunks_created: int
    processing_time_seconds: float
    message: str


class HealthResponse(BaseModel):
    """Response model for health check."""
    overall_status: str
    components: Dict[str, Any]
    timestamp: float


class DocumentInfo(BaseModel):
    """Information about processed documents."""
    filename: str
    chunks_count: int
    pages: List[int]
    processing_date: float


# Dependency to get orchestrator instance
async def get_orchestrator() -> MVPOrchestrator:
    """Get the global orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Service not ready. Orchestrator not initialized."
        )
    return orchestrator


# API endpoints
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global orchestrator
    
    try:
        logger.info("Initializing Annual Report Analyzer API...")
        
        # Validate configuration
        if not config.validate_azure_config():
            raise RuntimeError("Azure OpenAI configuration is invalid. Please check your environment variables.")
        
        # Setup directories
        config.setup_directories()
        
        # Initialize orchestrator
        orchestrator = MVPOrchestrator()
        
        # Perform health check
        health = await orchestrator.health_check()
        if health["overall_status"] != "healthy":
            logger.warning(f"Some components are not healthy: {health}")
        
        logger.info("API startup completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize API: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown."""
    logger.info("Shutting down Annual Report Analyzer API...")


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Annual Report Analyzer API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(orchestrator: MVPOrchestrator = Depends(get_orchestrator)):
    """
    Comprehensive health check of all system components.
    """
    try:
        health_result = await orchestrator.health_check()
        
        status_code = 200
        if health_result["overall_status"] == "degraded":
            status_code = 202  # Accepted but degraded
        elif health_result["overall_status"] == "unhealthy":
            status_code = 503  # Service unavailable
        
        return JSONResponse(
            status_code=status_code,
            content=health_result
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "overall_status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )


@app.post("/documents/upload", response_model=ProcessingResponse)
async def upload_document(
    file: UploadFile = File(...),
    orchestrator: MVPOrchestrator = Depends(get_orchestrator)
):
    """
    Upload and process a PDF document for analysis.
    """
    # Validate file
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )
    
    # Check file size (50MB limit)
    max_size = 50 * 1024 * 1024  # 50MB in bytes
    file_content = await file.read()
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size is 50MB, got {len(file_content) / (1024*1024):.1f}MB"
        )
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name
    
    try:
        logger.info(f"Processing uploaded document: {file.filename}")
        
        # Process document
        result = await orchestrator.process_document(temp_file_path)
        
        # Build response
        response = ProcessingResponse(
            status=result["status"],
            document_filename=result["document_filename"],
            total_pages=result["total_pages"],
            chunks_created=result["chunks_created"],
            processing_time_seconds=result["processing_time_seconds"],
            message=f"Successfully processed {result['document_filename']} with {result['chunks_created']} chunks"
        )
        
        logger.info(f"Document processing completed: {file.filename}")
        return response
        
    except Exception as e:
        logger.error(f"Document processing failed for {file.filename}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process document: {str(e)}"
        )
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_file_path)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary file: {e}")


@app.post("/documents/query", response_model=QueryResponse)
async def query_document(
    request: QueryRequest,
    orchestrator: MVPOrchestrator = Depends(get_orchestrator)
):
    """
    Query processed documents and get AI-generated answers with citations.
    """
    try:
        logger.info(f"Processing query: {request.question[:100]}...")
        
        # Process query
        result = await orchestrator.query_document(
            query=request.question,
            top_k=request.top_k
        )
        
        if result["status"] == "no_results":
            return QueryResponse(
                status="no_results",
                query=request.question,
                answer=result["answer"],
                citations=[],
                confidence=0.0,
                metadata={"message": "No relevant information found"}
            )
        
        # Convert citations to response model
        citations = [
            Citation(
                citation_id=cit["citation_id"],
                source_document=cit["source_document"],
                page_numbers=cit["page_numbers"],
                relevance_score=cit["relevance_score"],
                text_preview=cit["text_preview"]
            )
            for cit in result["citations"]
        ]
        
        response = QueryResponse(
            status=result["status"],
            query=result["query"],
            answer=result["answer"],
            citations=citations,
            confidence=result["confidence"],
            metadata=result["metadata"]
        )
        
        logger.info(f"Query processed successfully: {len(result['answer'])} chars answer")
        return response
        
    except ValueError as e:
        # Handle case where no documents are processed
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )


@app.get("/documents", response_model=List[DocumentInfo])
async def list_processed_documents(orchestrator: MVPOrchestrator = Depends(get_orchestrator)):
    """
    Get list of all processed documents.
    """
    try:
        documents = orchestrator.get_processed_documents()
        
        return [
            DocumentInfo(
                filename=doc["filename"],
                chunks_count=doc["chunks_count"],
                pages=doc["pages"],
                processing_date=doc["processing_date"]
            )
            for doc in documents
        ]
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve document list: {str(e)}"
        )


@app.get("/stats", response_model=Dict[str, Any])
async def get_system_stats(orchestrator: MVPOrchestrator = Depends(get_orchestrator)):
    """
    Get system statistics and metrics.
    """
    try:
        vector_stats = orchestrator.vector_store.get_stats()
        processed_docs = orchestrator.get_processed_documents()
        
        stats = {
            "vector_store": vector_stats,
            "processed_documents_count": len(processed_docs),
            "total_pages_processed": sum(len(doc["pages"]) for doc in processed_docs),
            "api_version": "1.0.0",
            "system_ready": vector_stats["total_vectors"] > 0
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with proper logging."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status_code": exc.status_code}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "status_code": 500}
    )


def create_app() -> FastAPI:
    """Factory function to create FastAPI app."""
    return app


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "src.api.fastapi_app:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.debug,
        log_level="info"
    )
