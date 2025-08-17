#!/usr/bin/env python3

import asyncio
from src.rag.vector_store import ChromaVectorStore
from src.utils.config import get_config
from src.azure.embedding_client import AzureEmbeddingClient

async def debug_similarity():
    # Load config and create components
    config = get_config()
    vector_store = ChromaVectorStore(persist_directory=config.rag.persist_directory)
    embedding_client = AzureEmbeddingClient(
        endpoint=config.azure_openai.endpoint,
        api_key=config.azure_openai.api_key,
        deployment_name=config.azure_openai.embedding_deployment
    )
    
    print("=== Debug Similarity Search ===")
    print(f"Vector store stats: {vector_store.get_stats()}")
    print(f"Score threshold from config: {config.rag.score_threshold}")
    print()
    
    # Test with a real query
    query = "financial performance"
    print(f"Testing query: '{query}'")
    
    # Generate embedding for the query
    query_embeddings = await embedding_client.get_embeddings([query])
    query_embedding = query_embeddings[0]
    print(f"Query embedding generated: {len(query_embedding)} dimensions")
    print()
    
    # Test similarity search without threshold
    print("=== Testing without score threshold ===")
    results = vector_store.similarity_search(query_embedding, k=5, score_threshold=None)
    print(f"Results without threshold: {len(results)}")
    
    for i, hit in enumerate(results[:3]):
        distance = hit["distance"]
        similarity = 1.0 - distance
        print(f"  Hit {i+1}: distance={distance:.4f}, similarity={similarity:.4f}")
        print(f"    Text preview: {hit['document'][:100]}...")
        print()
    
    # Test with different thresholds
    print("=== Testing with different thresholds ===")
    for threshold in [0.9, 0.8, 0.7, 0.5, 0.3, 0.1]:
        results = vector_store.similarity_search(query_embedding, k=5, score_threshold=threshold)
        print(f"Threshold {threshold}: {len(results)} results")
    
    print()
    print("=== Testing with very general query ===")
    general_query = "report"
    general_embeddings = await embedding_client.get_embeddings([general_query])
    general_embedding = general_embeddings[0]
    
    results = vector_store.similarity_search(general_embedding, k=3, score_threshold=None)
    print(f"Results for '{general_query}': {len(results)}")
    for i, hit in enumerate(results):
        distance = hit["distance"]
        similarity = 1.0 - distance
        print(f"  Hit {i+1}: distance={distance:.4f}, similarity={similarity:.4f}")

if __name__ == "__main__":
    asyncio.run(debug_similarity())
