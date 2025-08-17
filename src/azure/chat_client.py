"""
Azure OpenAI Chat Client for MVP implementation.
Handles chat completions with context and citation support.
"""

import asyncio
import time
from typing import List, Dict, Any, Optional
from openai import AsyncAzureOpenAI
from dataclasses import dataclass

from src.utils.logging_config import get_logger, LoggerMixin, log_performance, log_error


@dataclass
class ChatMessage:
    """Represents a chat message."""
    role: str
    content: str


@dataclass
class ChatResponse:
    """Represents a chat response with metadata."""
    content: str
    usage: Dict[str, int]
    model: str
    finish_reason: str


class AzureChatClient(LoggerMixin):
    """
    Azure OpenAI chat client for generating answers from context.
    """
    
    def __init__(
        self,
        endpoint: str,
        api_key: str,
        deployment_name: str,
        api_version: str = "2024-02-01",
        max_tokens: int = 4000,
        temperature: float = 0.1,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize Azure OpenAI chat client.
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: API key for authentication
            deployment_name: Name of the chat deployment
            api_version: API version to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0 - 1.0)
            max_retries: Maximum number of retries on failure
            retry_delay: Base delay between retries in seconds
        """
        self.endpoint = endpoint
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        
        # Initialize Azure OpenAI client
        self.client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        self.logger.info(
            "Azure chat client initialized",
            endpoint=endpoint,
            deployment=deployment_name,
            api_version=api_version,
            max_tokens=max_tokens,
            temperature=temperature
        )
    
    async def generate_answer(
        self, 
        context: str, 
        query: str,
        system_prompt: Optional[str] = None,
        include_citations: bool = True
    ) -> ChatResponse:
        """
        Generate an answer based on context and query.
        
        Args:
            context: Relevant context from document retrieval
            query: User's question
            system_prompt: Optional custom system prompt
            include_citations: Whether to include citation instructions
            
        Returns:
            ChatResponse with generated answer and metadata
            
        Raises:
            Exception: If chat completion fails after retries
        """
        start_time = time.time()
        
        try:
            # Build messages
            messages = self._build_messages(context, query, system_prompt, include_citations)
            
            # Generate completion
            response = await self._generate_completion(messages)
            
            duration = time.time() - start_time
            self.logger.info(
                "Answer generated successfully",
                **log_performance(
                    "generate_answer",
                    duration,
                    prompt_tokens=response.usage.get("prompt_tokens", 0),
                    completion_tokens=response.usage.get("completion_tokens", 0),
                    total_tokens=response.usage.get("total_tokens", 0)
                )
            )
            
            return response
            
        except Exception as e:
            self.logger.error(
                "Failed to generate answer",
                **log_error(e, {
                    "query_length": len(query),
                    "context_length": len(context)
                })
            )
            raise
    
    def _build_messages(
        self, 
        context: str, 
        query: str,
        system_prompt: Optional[str] = None,
        include_citations: bool = True
    ) -> List[ChatMessage]:
        """
        Build chat messages for the completion request.
        
        Args:
            context: Relevant context from document retrieval
            query: User's question
            system_prompt: Optional custom system prompt
            include_citations: Whether to include citation instructions
            
        Returns:
            List of formatted chat messages
        """
        if system_prompt is None:
            system_prompt = self._get_default_system_prompt(include_citations)
        
        # Build user message with context and query
        user_message = f"""Context:
{context}

Question: {query}

Please provide a comprehensive answer based on the context provided."""
        
        if include_citations:
            user_message += "\n\nMake sure to include specific references to page numbers or sections when available."
        
        return [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_message)
        ]
    
    def _get_default_system_prompt(self, include_citations: bool = True) -> str:
        """
        Get the default system prompt for financial document analysis.
        
        Args:
            include_citations: Whether to include citation instructions
            
        Returns:
            Default system prompt
        """
        base_prompt = """You are an expert financial analyst specializing in annual report analysis. Your role is to provide accurate, insightful answers based on the provided context from annual reports and financial documents.

Key instructions:
1. Base your answers strictly on the provided context
2. Be precise with financial figures and calculations
3. Explain financial concepts clearly for both expert and non-expert users
4. If information is not available in the context, clearly state this limitation
5. Provide specific, actionable insights when possible
6. Use professional financial terminology appropriately"""

        if include_citations:
            citation_prompt = """
7. Always include citations by referencing specific sections, pages, or document parts
8. Format citations clearly (e.g., "According to page 15 of the annual report...")
9. When quoting exact figures, reference the source table or section"""
            base_prompt += citation_prompt

        return base_prompt
    
    async def _generate_completion(self, messages: List[ChatMessage]) -> ChatResponse:
        """
        Generate chat completion with retries.
        
        Args:
            messages: List of chat messages
            
        Returns:
            ChatResponse with completion and metadata
        """
        for attempt in range(self.max_retries):
            try:
                # Convert messages to API format
                api_messages = [
                    {"role": msg.role, "content": msg.content}
                    for msg in messages
                ]
                
                response = await self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=api_messages,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=1.0,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                
                # Extract response data
                choice = response.choices[0]
                
                return ChatResponse(
                    content=choice.message.content,
                    usage=response.usage.model_dump() if response.usage else {},
                    model=response.model,
                    finish_reason=choice.finish_reason
                )
                
            except Exception as e:
                wait_time = self.retry_delay * (2 ** attempt)
                self.logger.warning(
                    f"Chat completion failed, attempt {attempt + 1}/{self.max_retries}",
                    error=str(e),
                    wait_time=wait_time
                )
                
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(wait_time)
                else:
                    raise
    
    def estimate_token_count(self, text: str) -> int:
        """
        Estimate token count for text (rough approximation).
        
        Args:
            text: Text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token for English text
        return len(text) // 4
    
    def validate_context_length(self, context: str, query: str, max_context_tokens: int = 6000) -> bool:
        """
        Validate that context and query fit within token limits.
        
        Args:
            context: Context text
            query: Query text
            max_context_tokens: Maximum allowed tokens for context + query
            
        Returns:
            True if within limits
        """
        total_tokens = self.estimate_token_count(context) + self.estimate_token_count(query)
        # Add buffer for system prompt and response
        return total_tokens <= max_context_tokens
    
    async def generate_summary(self, text: str, summary_type: str = "executive") -> ChatResponse:
        """
        Generate a summary of the provided text.
        
        Args:
            text: Text to summarize
            summary_type: Type of summary ("executive", "technical", "bullet_points")
            
        Returns:
            ChatResponse with summary
        """
        summary_prompts = {
            "executive": "Provide a concise executive summary highlighting key financial performance and strategic insights.",
            "technical": "Provide a detailed technical summary including specific metrics, calculations, and financial ratios.",
            "bullet_points": "Summarize the key points as clear, actionable bullet points."
        }
        
        prompt = summary_prompts.get(summary_type, summary_prompts["executive"])
        
        return await self.generate_answer(
            context=text,
            query=f"Please summarize this content. {prompt}",
            system_prompt="You are a financial analyst creating summaries of annual report content.",
            include_citations=False
        )
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check by testing chat completion.
        
        Returns:
            Dictionary with health check results
        """
        try:
            test_context = "The company's revenue was $100 million in 2024, up from $85 million in 2023."
            test_query = "What was the revenue growth rate?"
            
            start_time = time.time()
            response = await self.generate_answer(test_context, test_query)
            duration = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": duration,
                "response_length": len(response.content),
                "tokens_used": response.usage.get("total_tokens", 0),
                "test_passed": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "test_passed": False
            }


if __name__ == "__main__":
    # Test the chat client
    import asyncio
    from src.utils.config import get_config
    
    async def test_chat_client():
        config = get_config()
        
        client = AzureChatClient(
            endpoint=config.azure_openai.endpoint,
            api_key=config.azure_openai.api_key,
            deployment_name=config.azure_openai.chat_deployment,
            api_version=config.azure_openai.api_version,
            max_tokens=config.azure_openai.max_tokens,
            temperature=config.azure_openai.temperature
        )
        
        # Test answer generation
        context = """
        Revenue for fiscal year 2024 was $150 million, representing a 25% increase from 2023.
        Operating expenses were $120 million, up from $100 million in the previous year.
        Net income reached $30 million, compared to $20 million in 2023.
        """
        
        query = "What was the net profit margin in 2024 and how does it compare to 2023?"
        
        response = await client.generate_answer(context, query)
        print(f"Response: {response.content}")
        print(f"Tokens used: {response.usage}")
        
        # Test health check
        health = await client.health_check()
        print(f"Health check: {health}")
    
    # Run test if config is valid
    config = get_config()
    if config.validate_azure_config():
        asyncio.run(test_chat_client())
    else:
        print("Please configure Azure OpenAI settings in .env file")
