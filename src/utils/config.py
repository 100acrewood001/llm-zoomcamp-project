"""
Configuration management for Annual Report Analyzer MVP.
Handles loading configuration from YAML files and environment variables.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class AzureOpenAISettings(BaseSettings):
    """Azure OpenAI specific settings."""
    endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    api_key: str = Field(..., env="AZURE_OPENAI_API_KEY") 
    api_version: str = Field(default="2024-02-01", env="AZURE_OPENAI_API_VERSION")
    embedding_deployment: str = Field(default="text-embedding-ada-002", env="AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
    chat_deployment: str = Field(default="gpt-4", env="AZURE_OPENAI_CHAT_DEPLOYMENT")
    max_tokens: int = Field(default=4000)
    temperature: float = Field(default=0.1)


class RAGSettings(BaseSettings):
    """RAG system specific settings."""
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)
    top_k: int = Field(default=5)
    score_threshold: float = Field(default=0.7)
    persist_directory: str = Field(default="./data/faiss_index")


class APISettings(BaseSettings):
    """API server settings."""
    host: str = Field(default="0.0.0.0", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    debug: bool = Field(default=True, env="DEBUG")
    max_request_size_mb: int = Field(default=100)
    cors_origins: list = Field(default=["*"])


class Config:
    """Main configuration class that loads and manages all settings."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration from YAML file and environment variables.
        
        Args:
            config_path: Path to configuration YAML file
        """
        self.config_path = config_path or self._get_default_config_path()
        self._raw_config = self._load_yaml_config()
        
        # Initialize sub-configurations
        self.azure_openai = AzureOpenAISettings()
        self.rag = RAGSettings()
        self.api = APISettings()
        
        # Load additional settings from YAML
        self._load_yaml_settings()
    
    def _get_default_config_path(self) -> str:
        """Get default configuration file path."""
        current_dir = Path(__file__).parent.parent.parent
        return str(current_dir / "config" / "config.yaml")
    
    def _load_yaml_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file) or {}
        except FileNotFoundError:
            print(f"Warning: Config file {self.config_path} not found. Using defaults.")
            return {}
        except yaml.YAMLError as e:
            print(f"Error parsing YAML config: {e}")
            return {}
    
    def _load_yaml_settings(self):
        """Load additional settings from YAML that aren't covered by Pydantic."""
        # Override Pydantic settings with YAML values if present
        if azure_config := self._raw_config.get('azure', {}).get('openai', {}):
            for key, value in azure_config.items():
                if hasattr(self.azure_openai, key):
                    setattr(self.azure_openai, key, value)
        
        if rag_config := self._raw_config.get('rag', {}):
            # Update chunking settings
            if chunking_config := rag_config.get('chunking', {}):
                self.rag.chunk_size = chunking_config.get('chunk_size', self.rag.chunk_size)
                self.rag.chunk_overlap = chunking_config.get('chunk_overlap', self.rag.chunk_overlap)
            
            # Update retrieval settings  
            if retrieval_config := rag_config.get('retrieval', {}):
                self.rag.top_k = retrieval_config.get('top_k', self.rag.top_k)
                self.rag.score_threshold = retrieval_config.get('score_threshold', self.rag.score_threshold)
            
            # Update vector store settings
            if vs_config := rag_config.get('vector_store', {}):
                self.rag.persist_directory = vs_config.get('persist_directory', self.rag.persist_directory)
        
        if api_config := self._raw_config.get('api', {}):
            for key, value in api_config.items():
                if hasattr(self.api, key):
                    setattr(self.api, key, value)
    
    def get_raw_config(self, section: Optional[str] = None) -> Dict[str, Any]:
        """
        Get raw configuration dictionary.
        
        Args:
            section: Specific section to return, or None for full config
            
        Returns:
            Configuration dictionary
        """
        if section:
            return self._raw_config.get(section, {})
        return self._raw_config
    
    def validate_azure_config(self) -> bool:
        """
        Validate that Azure OpenAI configuration is properly set.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        required_fields = ['endpoint', 'api_key', 'embedding_deployment', 'chat_deployment']
        
        for field in required_fields:
            value = getattr(self.azure_openai, field, None)
            if not value or value.startswith('your-') or value == 'your-api-key-here':
                print(f"Error: Azure OpenAI {field} is not properly configured")
                return False
        
        return True
    
    def setup_directories(self):
        """Create necessary directories for the application."""
        directories = [
            self.rag.persist_directory,
            "./data/documents",
            "./logs"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def load_environment_file(env_file: str = ".env"):
    """
    Load environment variables from .env file.
    
    Args:
        env_file: Path to environment file
    """
    from dotenv import load_dotenv
    
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print(f"Loaded environment variables from {env_file}")
    else:
        print(f"Warning: Environment file {env_file} not found")


if __name__ == "__main__":
    # Test configuration loading
    load_environment_file()
    test_config = Config()
    
    print("Configuration loaded successfully:")
    print(f"Azure OpenAI Endpoint: {test_config.azure_openai.endpoint}")
    print(f"Chunk Size: {test_config.rag.chunk_size}")
    print(f"API Port: {test_config.api.port}")
    print(f"Config Valid: {test_config.validate_azure_config()}")
