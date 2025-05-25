from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):

    APP_NAME: str = "Mini-RAG-App"
    APP_VERSION: str = "1.0.0"
    OPENAI_API_KEY: str = "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"

    FILE_ALLOWED_TYPES: list = ["pdf", "docx", "txt"]
    FILE_MAX_SIZE: int = 10485760  # 10MB
    FILE_DEFAULT_CHUNK_SIZE: int = 1000

    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DATABASE: str = "mini_rag_app"
    
    GENERATION_BACKEND: str = "openai"
    EMBEDDING_BACKEND: str = "openai"

    OPENAI_API_URL: str = "https://api.openai.com/v1"
    COHERE_API_KEY: str = "dummy-key-for-testing"
    
    GENERATION_MODEL_ID: str = "gpt-3.5-turbo"
    EMBEDDING_MODEL_ID: str = "text-embedding-ada-002"
    EMBEDDING_MODEL_SIZE: int = 1536
    INPUT_DEFAULT_MAX_CHARACTER: int = 4000
    GENERATION_DEFAULT_MAX_TOKENS: int = 7500
    GENERATION_DEFAULT_TEMPERATURE: float = 0.7

    VECTOR_DB_BACKEND: str = "chroma"
    VECTOR_DB_PATH: str = "./data/vectordb"
    VECTOR_DB_DISTANCE_METHOD: str = "cosine"

    PRIMARY_LANG: str = "english"
    DEFAULT_LANG: str = "english"

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()