"""Embeddings module for generating document embeddings."""

from typing import List
from openai import OpenAI, APIError
from app.config import get_config


_client: OpenAI = None


def _get_openai_client() -> OpenAI:
    """Get or create OpenAI client singleton."""
    global _client
    
    if _client is None:
        config = get_config()
        if not config.openai_api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")
        _client = OpenAI(api_key=config.openai_api_key)
    
    return _client


def embed_text(text: str) -> List[float]:
    """Generate embedding for a single text.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector (list of floats)
        
    Raises:
        ValueError: If text is empty or embedding generation fails
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    config = get_config()
    client = _get_openai_client()
    
    try:
        response = client.embeddings.create(
            input=text.strip(),
            model=config.embedding_model
        )
        return response.data[0].embedding
    except APIError as e:
        raise Exception(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate embedding: {str(e)}")


def embed_texts(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for multiple texts.
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of embedding vectors
        
    Raises:
        ValueError: If texts list is empty or any text fails
    """
    if not texts:
        raise ValueError("Texts list cannot be empty")
    
    # Filter out empty texts
    texts = [t.strip() for t in texts if t and t.strip()]
    
    if not texts:
        raise ValueError("All texts are empty")
    
    config = get_config()
    client = _get_openai_client()
    
    try:
        response = client.embeddings.create(
            input=texts,
            model=config.embedding_model
        )
        
        # Sort by index to maintain order
        sorted_embeddings = sorted(response.data, key=lambda x: x.index)
        return [item.embedding for item in sorted_embeddings]
    except APIError as e:
        raise Exception(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate embeddings: {str(e)}")
