"""Chat module for RAG interactions."""

from openai import OpenAI, APIError
from app.config import get_config
from app.retrieve import retrieve_context
from app.hybrid_search import retrieve_context_hybrid, hybrid_retrieve_context
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


def answer_question(question: str, debug: bool = False, search_mode: str = "hybrid") -> str:
    """Answer a question using RAG with configurable search mode.
    
    Process:
    1. Retrieve relevant context (using semantic, keyword, or hybrid search)
    2. Build prompt with context
    3. Generate response using LLM
    4. Return answer
    
    Args:
        question: The user's question
        debug: If True, print debug information
        search_mode: Search mode - "semantic", "keyword", or "hybrid" (default)
        
    Returns:
        Generated answer
        
    Raises:
        ValueError: If question is empty
        Exception: If retrieval or generation fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    config = get_config()
    
    # Retrieve context using hybrid search
    contexts, explanation = hybrid_retrieve_context(
        question, 
        mode=search_mode,
        debug=debug
    )
    
    if debug:
        if explanation:
            print(f"\n{explanation}\n")
        print(f"[DEBUG] Found {len(contexts)} relevant chunks")
        for i, ctx in enumerate(contexts, 1):
            similarity = ctx.get("similarity", 0)
            rrf_score = ctx.get("rrf_score", 0)
            rank = ctx.get("rank", 0)
            
            print(f"  [{i}] ", end="")
            if search_mode == "hybrid" and rrf_score > 0:
                print(f"RRF Score: {rrf_score:.4f}")
            elif search_mode == "semantic" and similarity > 0:
                print(f"Similarity: {similarity:.2%}")
            elif search_mode == "keyword" and rank > 0:
                print(f"Rank: {rank:.4f}")
            
            print(f"      Content: {ctx.get('content', '')[:100]}...")
    
    # Build prompt
    prompt = build_prompt(question, contexts)
    
    # Generate response
    answer = _generate_response(prompt, config.chat_model)
    
    return answer
