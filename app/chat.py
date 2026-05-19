"""Chat module for RAG interactions."""

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


def chat_with_rag(
    query: str,
    context: str,
    model: str,
    temperature: float = 0.7
) -> str:
    """Generate response using GPT with RAG context.
    
    Args:
        query: The user's question
        context: Retrieved context from documents
        model: Model name to use for generation
        temperature: Temperature for response generation
        
    Returns:
        Generated response text
        
    Raises:
        ValueError: If query is empty
        Exception: If API call fails
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    client = _get_openai_client()
    
    prompt = f"""You are a helpful assistant. Answer the question using the provided context.

Context:
{context}

Question: {query}

Answer:"""
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        
        return response.choices[0].message.content
    except APIError as e:
        raise Exception(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to generate response: {str(e)}")
