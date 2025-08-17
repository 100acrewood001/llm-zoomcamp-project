"""
Basic tests for MVP components.
Run with: pytest tests/
"""

import pytest
import asyncio
import os
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.utils.config import Config
from src.rag.chunking_strategy import BasicChunkingStrategy, Chunk
from src.extractors.text_extractor import TextExtractor, Document, Page


class TestConfiguration:
    """Test configuration management."""
    
    def test_config_loading(self):
        """Test that configuration loads without errors."""
        config = Config()
        assert config.rag.chunk_size > 0
        assert config.rag.chunk_overlap >= 0
        assert config.api.port > 0


class TestChunkingStrategy:
    """Test text chunking functionality."""
    
    def setup_method(self):
        """Setup test chunker."""
        self.chunker = BasicChunkingStrategy(
            chunk_size=200,
            chunk_overlap=50
        )
    
    def test_chunk_direct_text(self):
        """Test direct text chunking."""
        test_text = """
        Revenue Analysis
        
        Total revenue for fiscal year 2024 was $150 million, representing a 25% increase 
        from the previous year's $120 million. This growth was driven by strong performance 
        in our core business segments.
        
        The company maintains a strong balance sheet with total assets of $500 million 
        and manageable debt levels. Our financial position remains solid.
        """
        
        chunks = self.chunker.chunk_text_directly(test_text, "test_doc")
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(len(chunk.text) <= 250 for chunk in chunks)  # Account for overlap
    
    def test_chunk_classification(self):
        """Test chunk content classification."""
        financial_text = "Revenue was $100 million with 25% profit margin"
        risk_text = "The company faces significant market risks and uncertainties"
        
        financial_type = self.chunker._classify_chunk_content(financial_text)
        risk_type = self.chunker._classify_chunk_content(risk_text)
        
        assert financial_type in ['financial_text', 'financial_table']
        assert risk_type == 'risk_factors'


class TestTextExtractor:
    """Test PDF text extraction."""
    
    def setup_method(self):
        """Setup test extractor."""
        self.extractor = TextExtractor(max_file_size_mb=10)
    
    def test_text_cleaning(self):
        """Test text cleaning functionality."""
        dirty_text = "  This   is   a    test   \n\n\n\n  with    extra   spaces  "
        cleaned = self.extractor.clean_text(dirty_text)
        
        assert "   " not in cleaned  # No triple spaces
        assert cleaned.startswith("This")  # Leading spaces removed
        assert cleaned.endswith("spaces")  # Trailing spaces removed
    
    def test_file_validation(self):
        """Test file validation."""
        # Test non-existent file
        with pytest.raises(FileNotFoundError):
            self.extractor._validate_file("non_existent.pdf")
        
        # Test wrong extension
        with pytest.raises(ValueError):
            self.extractor._validate_file("test.txt")


class TestAsyncComponents:
    """Test async components that require Azure OpenAI."""
    
    @pytest.mark.asyncio
    async def test_mock_embedding_generation(self):
        """Test embedding client interface (mocked)."""
        # This would test the embedding client with mocked responses
        # For now, just test that the imports work
        from src.azure.embedding_client import AzureEmbeddingClient
        from src.azure.chat_client import AzureChatClient
        
        # Test that classes can be instantiated (will fail without real config)
        assert AzureEmbeddingClient is not None
        assert AzureChatClient is not None


# Integration test (requires real configuration)
@pytest.mark.integration
class TestIntegration:
    """Integration tests that require real Azure OpenAI configuration."""
    
    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test complete pipeline if configuration is valid."""
        from src.utils.config import get_config, load_environment_file
        
        # Load environment
        load_environment_file()
        config = get_config()
        
        if not config.validate_azure_config():
            pytest.skip("Azure OpenAI configuration not available")
        
        # Test would go here with real document processing
        assert True  # Placeholder


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
