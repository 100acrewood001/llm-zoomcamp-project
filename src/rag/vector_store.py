"""
FAISS-based vector store for document embeddings.
Handles vector indexing, similarity search, and persistence.
"""

import os
import pickle
import numpy as np
import faiss
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import json
import time

from src.rag.chunking_strategy import Chunk
from src.utils.logging_config import get_logger, LoggerMixin, log_performance, log_error


class FAISSVectorStore(LoggerMixin):
    """
    FAISS-based vector store with persistence and metadata management.
    Optimized for annual report document chunks.
    """
    
    def __init__(
        self,
        embedding_dimension: int = 1536,  # Azure OpenAI ada-002 dimension
        index_type: str = "flat",
        persist_directory: str = "./data/faiss_index",
        similarity_metric: str = "cosine"
    ):
        """
        Initialize FAISS vector store.
        
        Args:
            embedding_dimension: Dimension of embeddings (1536 for ada-002)
            index_type: Type of FAISS index ("flat" or "ivf")
            persist_directory: Directory to persist index and metadata
            similarity_metric: Similarity metric ("cosine" or "l2")
        """
        self.embedding_dimension = embedding_dimension
        self.index_type = index_type
        self.persist_directory = persist_directory
        self.similarity_metric = similarity_metric
        
        # Create persist directory
        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize FAISS index
        self.index = self._create_index()
        
        # Metadata storage
        self.chunks_metadata: List[Dict[str, Any]] = []
        self.chunk_id_to_index: Dict[str, int] = {}
        
        # Index state
        self.is_trained = False
        self.total_vectors = 0
        
        self.logger.info(
            "FAISS vector store initialized",
            embedding_dimension=embedding_dimension,
            index_type=index_type,
            similarity_metric=similarity_metric,
            persist_directory=persist_directory
        )
    
    def _create_index(self) -> faiss.Index:
        """
        Create appropriate FAISS index based on configuration.
        
        Returns:
            FAISS index instance
        """
        if self.similarity_metric == "cosine":
            # For cosine similarity, we'll normalize vectors and use inner product
            if self.index_type == "flat":
                index = faiss.IndexFlatIP(self.embedding_dimension)
            else:  # ivf
                # For IVF, we need enough vectors to train (recommended: 30x nlist)
                nlist = 100
                quantizer = faiss.IndexFlatIP(self.embedding_dimension)
                index = faiss.IndexIVFFlat(quantizer, self.embedding_dimension, nlist)
        else:  # L2 distance
            if self.index_type == "flat":
                index = faiss.IndexFlatL2(self.embedding_dimension)
            else:  # ivf
                nlist = 100
                quantizer = faiss.IndexFlatL2(self.embedding_dimension)
                index = faiss.IndexIVFFlat(quantizer, self.embedding_dimension, nlist)
        
        return index
    
    def add_documents(self, chunks: List[Chunk], embeddings: List[np.ndarray]):
        """
        Add documents and their embeddings to the vector store.
        
        Args:
            chunks: List of document chunks
            embeddings: List of corresponding embeddings
            
        Raises:
            ValueError: If chunks and embeddings lists don't match
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) count mismatch")
        
        if not chunks:
            self.logger.warning("No chunks provided for indexing")
            return
        
        start_time = time.time()
        
        try:
            # Convert embeddings to numpy array
            embedding_matrix = np.array(embeddings, dtype=np.float32)
            
            # Normalize embeddings for cosine similarity if needed
            if self.similarity_metric == "cosine":
                faiss.normalize_L2(embedding_matrix)
            
            # Train index if needed (for IVF indices)
            if self.index_type == "ivf" and not self.is_trained:
                min_train_size = 300  # Minimum vectors needed for IVF training
                if len(embeddings) >= min_train_size:
                    self.logger.info(f"Training IVF index with {len(embeddings)} vectors")
                    self.index.train(embedding_matrix)
                    self.is_trained = True
                else:
                    self.logger.warning(
                        f"Not enough vectors to train IVF index (have {len(embeddings)}, need {min_train_size}). "
                        f"Using flat index for now."
                    )
                    # Fall back to flat index
                    self._fallback_to_flat_index()
            
            # Add vectors to index
            start_index = self.total_vectors
            self.index.add(embedding_matrix)
            self.total_vectors += len(embeddings)
            
            # Store metadata
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    "chunk_id": chunk.chunk_id,
                    "text": chunk.text,
                    "source_document": chunk.source_document,
                    "page_numbers": chunk.page_numbers,
                    "metadata": chunk.metadata,
                    "vector_index": start_index + i,
                    "embedding_dimension": len(embeddings[i]),
                    "added_timestamp": time.time()
                }
                
                self.chunks_metadata.append(chunk_metadata)
                self.chunk_id_to_index[chunk.chunk_id] = start_index + i
            
            duration = time.time() - start_time
            self.logger.info(
                "Documents added to vector store",
                **log_performance(
                    "add_documents",
                    duration,
                    chunks_added=len(chunks),
                    total_vectors=self.total_vectors,
                    index_type=self.index_type
                )
            )
            
        except Exception as e:
            self.logger.error(
                "Failed to add documents to vector store",
                **log_error(e, {"chunks_count": len(chunks)})
            )
            raise
    
    def _fallback_to_flat_index(self):
        """Fallback to flat index if IVF training fails."""
        self.logger.info("Falling back to flat index")
        
        # Save existing vectors if any
        existing_vectors = []
        if self.total_vectors > 0:
            existing_vectors = self.index.reconstruct_n(0, self.total_vectors)
        
        # Create new flat index
        self.index = self._create_flat_index()
        self.index_type = "flat"
        
        # Re-add existing vectors
        if len(existing_vectors) > 0:
            self.index.add(np.array(existing_vectors, dtype=np.float32))
    
    def _create_flat_index(self) -> faiss.Index:
        """Create flat index as fallback."""
        if self.similarity_metric == "cosine":
            return faiss.IndexFlatIP(self.embedding_dimension)
        else:
            return faiss.IndexFlatL2(self.embedding_dimension)
    
    def similarity_search(
        self, 
        query_embedding: np.ndarray, 
        k: int = 5,
        score_threshold: Optional[float] = None
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Perform similarity search for query embedding.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of similar documents to return
            score_threshold: Minimum similarity score threshold
            
        Returns:
            List of tuples (chunk_metadata, similarity_score)
        """
        if self.total_vectors == 0:
            self.logger.warning("No vectors in index for similarity search")
            return []
        
        start_time = time.time()
        
        try:
            # Ensure query embedding is correct shape and type
            query_vector = np.array([query_embedding], dtype=np.float32)
            
            # Normalize for cosine similarity if needed
            if self.similarity_metric == "cosine":
                faiss.normalize_L2(query_vector)
            
            # Perform search
            k = min(k, self.total_vectors)  # Don't search for more vectors than we have
            scores, indices = self.index.search(query_vector, k)
            
            # Process results
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx == -1:  # FAISS returns -1 for empty results
                    break
                
                # Apply score threshold if specified
                if score_threshold is not None:
                    if self.similarity_metric == "cosine" and score < score_threshold:
                        break
                    elif self.similarity_metric == "l2" and score > score_threshold:
                        break
                
                # Get chunk metadata
                chunk_metadata = self.chunks_metadata[idx].copy()
                
                # Convert similarity score if needed (for cosine, higher is better)
                final_score = float(score)
                if self.similarity_metric == "l2":
                    # Convert L2 distance to similarity (lower distance = higher similarity)
                    final_score = 1.0 / (1.0 + score)
                
                results.append((chunk_metadata, final_score))
            
            duration = time.time() - start_time
            self.logger.debug(
                "Similarity search completed",
                **log_performance(
                    "similarity_search",
                    duration,
                    k=k,
                    results_count=len(results),
                    total_vectors=self.total_vectors
                )
            )
            
            return results
            
        except Exception as e:
            self.logger.error(
                "Similarity search failed",
                **log_error(e, {"k": k, "total_vectors": self.total_vectors})
            )
            raise
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Get chunk metadata by chunk ID.
        
        Args:
            chunk_id: ID of the chunk to retrieve
            
        Returns:
            Chunk metadata or None if not found
        """
        if chunk_id in self.chunk_id_to_index:
            index = self.chunk_id_to_index[chunk_id]
            return self.chunks_metadata[index].copy()
        return None
    
    def save_index(self, index_path: Optional[str] = None) -> str:
        """
        Save FAISS index and metadata to disk.
        
        Args:
            index_path: Optional custom path for index files
            
        Returns:
            Path where index was saved
        """
        if index_path is None:
            index_path = os.path.join(self.persist_directory, "faiss_index.index")
        
        start_time = time.time()
        
        try:
            # Save FAISS index
            faiss.write_index(self.index, index_path)
            
            # Save metadata
            metadata_path = index_path.replace(".index", "_metadata.json")
            metadata = {
                "chunks_metadata": self.chunks_metadata,
                "chunk_id_to_index": self.chunk_id_to_index,
                "total_vectors": self.total_vectors,
                "embedding_dimension": self.embedding_dimension,
                "index_type": self.index_type,
                "similarity_metric": self.similarity_metric,
                "is_trained": self.is_trained,
                "save_timestamp": time.time()
            }
            
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            duration = time.time() - start_time
            self.logger.info(
                "Vector store saved successfully",
                **log_performance(
                    "save_index",
                    duration,
                    index_path=index_path,
                    total_vectors=self.total_vectors
                )
            )
            
            return index_path
            
        except Exception as e:
            self.logger.error(
                "Failed to save vector store",
                **log_error(e, {"index_path": index_path})
            )
            raise
    
    def load_index(self, index_path: Optional[str] = None) -> bool:
        """
        Load FAISS index and metadata from disk.
        
        Args:
            index_path: Optional custom path for index files
            
        Returns:
            True if successfully loaded, False otherwise
        """
        if index_path is None:
            index_path = os.path.join(self.persist_directory, "faiss_index.index")
        
        if not os.path.exists(index_path):
            self.logger.warning(f"Index file not found: {index_path}")
            return False
        
        start_time = time.time()
        
        try:
            # Load FAISS index
            self.index = faiss.read_index(index_path)
            
            # Load metadata
            metadata_path = index_path.replace(".index", "_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                self.chunks_metadata = metadata["chunks_metadata"]
                self.chunk_id_to_index = metadata["chunk_id_to_index"]
                self.total_vectors = metadata["total_vectors"]
                self.is_trained = metadata.get("is_trained", False)
                
                # Validate loaded configuration
                if metadata["embedding_dimension"] != self.embedding_dimension:
                    self.logger.warning(
                        f"Embedding dimension mismatch: expected {self.embedding_dimension}, "
                        f"got {metadata['embedding_dimension']}"
                    )
            
            duration = time.time() - start_time
            self.logger.info(
                "Vector store loaded successfully",
                **log_performance(
                    "load_index",
                    duration,
                    index_path=index_path,
                    total_vectors=self.total_vectors
                )
            )
            
            return True
            
        except Exception as e:
            self.logger.error(
                "Failed to load vector store",
                **log_error(e, {"index_path": index_path})
            )
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get vector store statistics.
        
        Returns:
            Dictionary with store statistics
        """
        return {
            "total_vectors": self.total_vectors,
            "embedding_dimension": self.embedding_dimension,
            "index_type": self.index_type,
            "similarity_metric": self.similarity_metric,
            "is_trained": self.is_trained,
            "unique_documents": len(set(chunk["source_document"] for chunk in self.chunks_metadata)),
            "chunks_count": len(self.chunks_metadata),
            "persist_directory": self.persist_directory
        }
    
    def clear(self):
        """Clear all vectors and metadata from the store."""
        self.index = self._create_index()
        self.chunks_metadata = []
        self.chunk_id_to_index = {}
        self.total_vectors = 0
        self.is_trained = False
        
        self.logger.info("Vector store cleared")


if __name__ == "__main__":
    # Test vector store
    import numpy as np
    
    # Create test vector store
    vector_store = FAISSVectorStore(
        embedding_dimension=5,  # Small dimension for testing
        persist_directory="./test_data/faiss_test"
    )
    
    # Create test chunks and embeddings
    from src.rag.chunking_strategy import Chunk
    
    test_chunks = [
        Chunk(
            text="Revenue increased by 25% this quarter",
            chunk_id="test_1",
            source_document="test.pdf",
            page_numbers=[1],
            start_char=0,
            end_char=35,
            metadata={"type": "financial"}
        ),
        Chunk(
            text="Operating expenses remained stable",
            chunk_id="test_2", 
            source_document="test.pdf",
            page_numbers=[1],
            start_char=36,
            end_char=70,
            metadata={"type": "financial"}
        )
    ]
    
    test_embeddings = [
        np.random.rand(5).astype(np.float32),
        np.random.rand(5).astype(np.float32)
    ]
    
    # Test adding documents
    vector_store.add_documents(test_chunks, test_embeddings)
    print(f"Added {vector_store.total_vectors} vectors")
    
    # Test similarity search
    query_embedding = np.random.rand(5).astype(np.float32)
    results = vector_store.similarity_search(query_embedding, k=2)
    
    print(f"\nSimilarity search results ({len(results)}):")
    for chunk_metadata, score in results:
        print(f"  Score: {score:.4f}, Text: {chunk_metadata['text'][:50]}...")
    
    # Test save/load
    save_path = vector_store.save_index()
    print(f"\nSaved index to: {save_path}")
    
    # Test stats
    stats = vector_store.get_stats()
    print(f"\nVector store stats: {stats}")
