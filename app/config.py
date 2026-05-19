"""Configuration module for RAG application."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Config:
    """Application configuration."""
    
    # OpenAI
    openai_api_key: str
    embedding_model: str
    chat_model: str
    
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # Chunking
    chunk_size: int
    chunk_overlap: int
    
    # Retrieval
    top_k: int
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            embedding_model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            chat_model=os.getenv("CHAT_MODEL", "gpt-4o-mini"),
            supabase_url=os.getenv("SUPABASE_URL", ""),
            supabase_key=os.getenv("SUPABASE_KEY", ""),
            chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200")),
            top_k=int(os.getenv("TOP_K", "5")),
        )


def get_config() -> Config:
    """Get application configuration."""
    return Config.from_env()
