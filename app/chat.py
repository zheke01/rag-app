"""Chat module for RAG interactions."""

from openai import OpenAI, APIError
from app.config import get_config
from app.retrieve import retrieve_context
from app.prompt_builder import build_prompt


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


def _generate_response(prompt: str, model: str, temperature: float = 0.7) -> str:
    """Generate response using OpenAI Chat API.
    
    Args:
        prompt: The complete prompt
        model: Model name to use
        temperature: Temperature for generation
        
    Returns:
        Generated response text
    """
    client = _get_openai_client()
    
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


def answer_question(question: str, debug: bool = False) -> str:
    """Answer a question using RAG.
    
    Process:
    1. Retrieve relevant context
    2. Build prompt with context
    3. Generate response using LLM
    4. Return answer
    
    Args:
        question: The user's question
        debug: If True, print debug information
        
    Returns:
        Generated answer
        
    Raises:
        ValueError: If question is empty
        Exception: If retrieval or generation fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    config = get_config()
    
    # Retrieve context
    contexts = retrieve_context(question)
    
    if debug:
        print(f"\n[DEBUG] Found {len(contexts)} relevant chunks")
        for i, ctx in enumerate(contexts, 1):
            similarity = ctx.get("similarity", 0)
            print(f"  [{i}] Similarity: {similarity:.2%}")
            print(f"      Content: {ctx.get('content', '')[:100]}...")
    
    # Build prompt
    prompt = build_prompt(question, contexts)
    
    # Generate response
    answer = _generate_response(prompt, config.chat_model)
    
    return answer
