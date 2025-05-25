from pydantic_settings import BaseSettings
from typing import Optional, List, Dict, Any
import os
from functools import lru_cache
import json

class Settings(BaseSettings):
    # Base application settings
    APP_NAME: str = "Mini RAG App"
    DEBUG: bool = True
    app_version: str = "0.1"
    
    # MongoDB settings
    MONGODB_URL: str = "mongodb://localhost:27017/"
    MONGODB_DB_NAME: str = "mini_rag_db"
    MONGODB_DATABASE: str = "mini_rag_db"  # Alias for compatibility with main.py
    
    # Vector DB settings
    VECTOR_DB_TYPE: str = "qdrant"  # Options: "chroma", "qdrant", "pinecone"
    VECTOR_DB_URL: Optional[str] = None
    VECTOR_DB_KEY: Optional[str] = None
    VECTOR_DB_BACKEND: str = "qdrant"  # Alias for compatibility with main.py
    vector_db_path: str = "qdrant_db"
    vector_db_distance_method: str = "cosine"
    
    # LLM settings
    LLM_PROVIDER_TYPE: str = "openai"  # Options: "openai", "huggingface", "anthropic", "local"
    LLM_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL_NAME: str = "gpt-3.5-turbo"
    
    # OpenAI settings
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY", "")
    openai_api_url: str = "https://api.openai.com/v1"
    
    # Cohere settings
    cohere_api_key: Optional[str] = ""
    
    # Generation and embedding models
    GENERATION_BACKEND: str = "openai"  # Provider for text generation
    GENERATION_MODEL_ID: str = "gpt-3.5-turbo"  # Model ID for text generation
    EMBEDDING_BACKEND: str = "openai"  # Provider for embeddings
    EMBEDDING_MODEL_ID: str = "text-embedding-3-small"  # Model ID for embeddings
    EMBEDDING_MODEL_SIZE: int = 1536  # Dimension of embeddings
    generation_default_max_tokens: int = 7500
    generation_default_temperature: float = 0.1
    input_default_max_character: int = 1024
    
    # Language settings
    PRIMARY_LANG: str = "en"  # Primary language for templates
    DEFAULT_LANG: str = "en"  # Default fallback language
    DEFAULT_LANGUAGE: str = "en"  # Alias for compatibility
    SUPPORTED_LANGUAGES: List[str] = ["en", "ar"]
    
    # File storage settings
    FILE_UPLOAD_PATH: str = "./uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    file_max_size: int = 10  # In MB
    file_default_chunk_size: int = 512000  # in bytes
    file_allowed_types: List[str] = ["text/plain", "application/pdf"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
            if field_name == "file_allowed_types" and raw_val.startswith("["):
                try:
                    return json.loads(raw_val)
                except:
                    return raw_val
            return raw_val

@lru_cache()
def get_settings() -> Settings:
    """Returns the settings instance, cached for performance."""
    return Settings() 