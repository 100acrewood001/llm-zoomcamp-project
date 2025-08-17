#!/usr/bin/env python3

import asyncio
from src.orchestrator.mvp_orchestrator import MVPOrchestrator

async def test_real_query():
    orchestrator = MVPOrchestrator()
    
    # Generate a real embedding for a relevant query
    query = 'financial performance'
    query_embeddings = await orchestrator.embedding_client.get_embeddings([query])
    query_embedding = query_embeddings[0]
    
    print(f'Query: {query}')
    print(f'Embedding dimensions: {len(query_embedding)}')
    
    # Test similarity search with the real embedding
    search_results = orchestrator.vector_store.similarity_search(query_embedding, k=3, score_threshold=None)
    print(f'Results without threshold: {len(search_results)}')
    
    if search_results:
        for i, hit in enumerate(search_results[:3]):
            distance = hit['distance'] 
            similarity = 1.0 - distance
            print(f'Hit {i+1}: distance={distance:.4f}, similarity={similarity:.4f}')
            print(f'  Text preview: {hit["document"][:100]}...')
        
        # Test with threshold 0.5
        search_results_thresh = orchestrator.vector_store.similarity_search(query_embedding, k=3, score_threshold=0.5)
        print(f'Results with threshold 0.5: {len(search_results_thresh)}')
        
        # Test with threshold 0.3
        search_results_thresh = orchestrator.vector_store.similarity_search(query_embedding, k=3, score_threshold=0.3)
        print(f'Results with threshold 0.3: {len(search_results_thresh)}')
    else:
        print('No results found - this indicates a problem!')

if __name__ == "__main__":
    asyncio.run(test_real_query())
