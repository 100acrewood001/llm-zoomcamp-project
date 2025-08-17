
"""
ChromaDB-based vector store for document embeddings.
Handles vector indexing, similarity search, and persistence using ChromaDB and LangChain.
"""

from typing import List, Dict, Any, Optional
from src.rag.chunking_strategy import Chunk
from src.utils.logging_config import get_logger, LoggerMixin

# ChromaDB and LangChain imports
import chromadb
from chromadb.config import Settings
from langchain_community.vectorstores import Chroma

class ChromaVectorStore(LoggerMixin):
    """
    ChromaDB-based vector store with persistence and metadata management.
    Designed for easy migration to managed vector DBs (e.g., Azure AI Search, Pinecone).
    """
    def __init__(self, persist_directory: str = "./data/chroma_index"):
        self.persist_directory = persist_directory
        self.logger.info("Chroma vector store initialized", persist_directory=persist_directory)
        self._client = chromadb.PersistentClient(path=persist_directory, settings=Settings(allow_reset=True))
        self._collection = self._client.get_or_create_collection("default")

    def add_documents(self, chunks: List[Chunk], embeddings: List[list]):
        """
        Add documents and their embeddings to the vector store.
        Args:
            chunks: List of document chunks
            embeddings: List of corresponding embeddings (as lists, not numpy arrays)
        """
        if len(chunks) != len(embeddings):
            raise ValueError(f"Chunks ({len(chunks)}) and embeddings ({len(embeddings)}) count mismatch")
        if not chunks:
            self.logger.warning("No chunks provided for indexing")
            return
        ids = [chunk.chunk_id for chunk in chunks]
        metadatas = []
        
        for chunk in chunks:
            # Convert page_numbers list to string for ChromaDB compatibility
            page_numbers_str = ",".join(map(str, chunk.page_numbers)) if chunk.page_numbers else "1"
            
            # Build metadata dict with ChromaDB-compatible values
            metadata = {
                "source_document": chunk.source_document,
                "page_numbers": page_numbers_str,  # Convert list to comma-separated string
            }
            
            # Add chunk metadata, ensuring all values are ChromaDB-compatible
            if chunk.metadata:
                for key, value in chunk.metadata.items():
                    # Convert complex types to strings
                    if isinstance(value, (list, dict)):
                        metadata[key] = str(value)
                    elif isinstance(value, (str, int, float, bool)) or value is None:
                        metadata[key] = value
                    else:
                        # Convert any other type to string
                        metadata[key] = str(value)
            
            metadatas.append(metadata)
        
        documents = [chunk.text for chunk in chunks]
        self._collection.add(
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        self.logger.info("Documents added to Chroma vector store", count=len(chunks))

    def similarity_search(self, query_embedding: list, k: int = 5, score_threshold: float = None) -> List[Dict[str, Any]]:
        """
        Perform similarity search for query embedding.
        Args:
            query_embedding: Query embedding vector (as list)
            k: Number of similar documents to return
            score_threshold: Minimum similarity score threshold (optional)
        Returns:
            List of dicts with document, metadata, and distance
        """
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"]
        )
        hits = []
        for i in range(len(results["ids"][0])):
            distance = results["distances"][0][i]
            
            # Apply score threshold if specified
            # Note: ChromaDB returns distances (lower is better), 
            # so we convert to similarity score (1 - distance) for threshold comparison
            similarity_score = 1.0 - distance
            if score_threshold is not None and similarity_score < score_threshold:
                continue
                
            hit = {
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": distance
            }
            hits.append(hit)
        self.logger.info("Similarity search completed", results_count=len(hits))
        return hits

    def clear(self):
        """Clear all vectors and metadata from the store."""
        self._client.reset()
        self._collection = self._client.get_or_create_collection("default")
        self.logger.info("Chroma vector store cleared")

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics."""
        count = self._collection.count()
        return {
            "total_vectors": count,
            "persist_directory": self.persist_directory
        }
    
    def get_documents_info(self) -> List[Dict[str, Any]]:
        """Get information about all stored documents."""
        try:
            # Query all documents from ChromaDB
            results = self._collection.get(include=["documents", "metadatas"])
            
            if not results["ids"]:
                return []
            
            # Group by source document
            docs_map = {}
            for i, doc_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i]
                source_doc = metadata.get("source_document", "unknown")
                
                if source_doc not in docs_map:
                    docs_map[source_doc] = {
                        "filename": source_doc,
                        "chunks": [],
                        "pages": set()
                    }
                
                # Parse page_numbers from string back to list
                page_numbers_str = metadata.get("page_numbers", "1")
                try:
                    page_numbers = [int(p.strip()) for p in page_numbers_str.split(",") if p.strip()]
                except (ValueError, AttributeError):
                    page_numbers = [1]
                
                docs_map[source_doc]["chunks"].append({
                    "chunk_id": doc_id,
                    "metadata": metadata
                })
                docs_map[source_doc]["pages"].update(page_numbers)
            
            # Convert to list format
            documents_info = []
            for doc_name, doc_data in docs_map.items():
                documents_info.append({
                    "filename": doc_name,
                    "chunks_count": len(doc_data["chunks"]),
                    "pages": sorted(list(doc_data["pages"])),
                    "processing_date": 0  # ChromaDB doesn't store timestamps by default
                })
            
            return documents_info
            
        except Exception as e:
            self.logger.error(f"Failed to get documents info: {e}")
            return []

if __name__ == "__main__":
    # Test vector store
    from src.rag.chunking_strategy import Chunk
    # Create test vector store
    vector_store = ChromaVectorStore(persist_directory="./test_data/chroma_test")
    # Create test chunks and embeddings
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
        [0.1, 0.2, 0.3, 0.4, 0.5],
        [0.5, 0.4, 0.3, 0.2, 0.1]
    ]
    # Test adding documents
    vector_store.add_documents(test_chunks, test_embeddings)
    print(f"Added {vector_store.get_stats()['total_vectors']} vectors")
    # Test similarity search
    query_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]
    results = vector_store.similarity_search(query_embedding, k=2)
    print(f"\nSimilarity search results ({len(results)}):")
    for hit in results:
        print(f"  Distance: {hit['distance']:.4f}, Text: {hit['document'][:50]}...")
    # Test stats
    stats = vector_store.get_stats()
    print(f"\nVector store stats: {stats}")
