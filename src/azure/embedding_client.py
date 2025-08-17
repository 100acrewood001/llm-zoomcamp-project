"""
Azure OpenAI Embedding Client for MVP implementation.
Handles embedding generation with rate limiting and error handling.
"""

import asyncio
import time
from typing import List, Optional, Dict, Any

import numpy as np
from openai import AsyncAzureOpenAI

from src.utils.logging_config import get_logger, LoggerMixin, log_performance, log_error


class AzureEmbeddingClient(LoggerMixin):
    """
    Azure OpenAI embedding client with rate limiting and batch processing.
    """
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment_name: str,
        api_version: str = "2024-02-01",
        max_concurrent_requests: int = 5,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Azure OpenAI embedding client.
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: API key for authentication
            deployment_name: Name of the embedding deployment
            api_version: API version to use
            max_concurrent_requests: Maximum concurrent requests
            max_retries: Maximum number of retries on failure
            retry_delay: Base delay between retries in seconds
        """
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.max_concurrent_requests = max_concurrent_requests
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize Azure OpenAI client
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        # Rate limiting
        self._semaphore = asyncio.Semaphore(max_concurrent_requests)
        self._last_request_time = 0
        self._min_request_interval = 0.1  # Minimum time between requests
        
        self.logger.info(
            "Azure embedding client initialized",
            endpoint=endpoint,
            deployment=deployment_name,
            api_version=api_version
        )
    
    async def get_embedding(self, text: str) -> np.ndarray:
        """
        Get embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array containing the embedding
            
        Raises:
            Exception: If embedding generation fails after retries
        """
        embeddings = await self.get_embeddings([text])
        return embeddings[0]
    
    async def get_embeddings(self, texts: List[str]) -> List[np.ndarray]:
        """
        Get embeddings for multiple texts with batching and rate limiting.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of numpy arrays containing embeddings
            
        Raises:
            Exception: If embedding generation fails after retries
        """
        if not texts:
            return []
        
        # Filter out empty texts
        valid_texts = [(i, text) for i, text in enumerate(texts) if text.strip()]
        if not valid_texts:
            self.logger.warning("All input texts are empty")
            return [np.array([]) for _ in texts]
        
        start_time = time.time()
        
        try:
            # Process in batches to avoid token limits
            batch_size = 20  # Azure OpenAI embedding batch limit
            all_embeddings = []
            
            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i:i + batch_size]
                batch_texts = [text for _, text in batch]
                
                batch_embeddings = await self._get_embeddings_batch(batch_texts)
                all_embeddings.extend(batch_embeddings)
            
            # Map embeddings back to original positions
            result = [None] * len(texts)
            for (original_idx, _), embedding in zip(valid_texts, all_embeddings):
                result[original_idx] = embedding
            
            # Fill empty positions with zero vectors
            if all_embeddings:
                embedding_dim = len(all_embeddings[0])
                for i, embedding in enumerate(result):
                    if embedding is None:
                        result[i] = np.zeros(embedding_dim)
            
            duration = time.time() - start_time
            self.logger.info(
                "Embeddings generated successfully",
                **log_performance(
                    "get_embeddings",
                    duration,
                    text_count=len(texts),
                    valid_text_count=len(valid_texts),
                    batch_count=(len(valid_texts) + batch_size - 1) // batch_size
                )
            )
            
            return result
            
        except Exception as e:
            self.logger.error(
                "Failed to generate embeddings",
                **log_error(e, {"text_count": len(texts)})
            )
            raise
    
    async def _get_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Get embeddings for a batch of texts with rate limiting and retries.
        
        Args:
            texts: List of texts to embed (within batch size limit)
            
        Returns:
            List of numpy arrays containing embeddings
        """
        async with self._semaphore:
            # Rate limiting
            await self._enforce_rate_limit()
            
            for attempt in range(self.max_retries):
                try:
                    response = await self.client.embeddings.create(
                        model=self.deployment_name,
                        input=texts
                    )
                    
                    embeddings = [
                        np.array(embedding.embedding, dtype=np.float32)
                        for embedding in response.data
                    ]
                    
                    self.logger.debug(
                        "Batch embeddings generated",
                        batch_size=len(texts),
                        attempt=attempt + 1
                    )
                    
                    return embeddings
                    
                except Exception as e:
                    wait_time = self.retry_delay * (2 ** attempt)
                    self.logger.warning(
                        f"Embedding request failed, attempt {attempt + 1}/{self.max_retries}",
                        error=str(e),
                        wait_time=wait_time
                    )
                    
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(wait_time)
                    else:
                        raise
    
    async def _enforce_rate_limit(self):
        """Enforce minimum time between requests."""
        current_time = time.time()
        time_since_last = current_time - self._last_request_time
        
        if time_since_last < self._min_request_interval:
            wait_time = self._min_request_interval - time_since_last
            await asyncio.sleep(wait_time)
        
        self._last_request_time = time.time()
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation).
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    def validate_text_length(self, text: str, max_tokens: int = 8192) -> bool:
        """
        Validate that text is within token limits.
        
        Args:
            text: Text to validate
            max_tokens: Maximum allowed tokens
            
        Returns:
            True if text is within limits
        """
        estimated_tokens = self.estimate_tokens(text)
        return estimated_tokens <= max_tokens
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check by testing embedding generation.
        
        Returns:
            Dictionary with health check results
        """
        try:
            test_text = "This is a health check test."
            start_time = time.time()
            
            embedding = await self.get_embedding(test_text)
            duration = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": duration,
                "embedding_dimension": len(embedding),
                "test_passed": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "test_passed": False
            }


if __name__ == "__main__":
    # Test the embedding client
    import asyncio
    from src.utils.config import get_config
    
    async def test_embedding_client():
        config = get_config()
        
        client = AzureEmbeddingClient(
            endpoint=config.azure_openai.endpoint,
            api_key=config.azure_openai.api_key,
            deployment_name=config.azure_openai.embedding_deployment,
            api_version=config.azure_openai.api_version
        )
        
        # Test single embedding
        text = "This is a test document about financial analysis."
        embedding = await client.get_embedding(text)
        print(f"Single embedding dimension: {len(embedding)}")
        
        # Test batch embeddings
        texts = [
            "Revenue increased by 15% this quarter.",
            "Operating expenses remained stable.",
            "The company faces competitive challenges."
        ]
        embeddings = await client.get_embeddings(texts)
        print(f"Batch embeddings count: {len(embeddings)}")
        
        # Test health check
        health = await client.health_check()
        print(f"Health check: {health}")
    
    # Run test if config is valid
    config = get_config()
    if config.validate_azure_config():
        asyncio.run(test_embedding_client())
    else:
        print("Please configure Azure OpenAI settings in .env file")
