"""Keyword search module using PostgreSQL full-text search."""

from typing import List, Dict
from app.db import get_supabase_client
from app.config import get_config


def search_by_keywords(query: str, top_k: int = None) -> List[Dict]:
    """Search documents using keyword/lexical search.
    
    Uses PostgreSQL full-text search (tsvector + tsquery) to find documents
    that contain the exact words from the query. Good for:
    - Technical terms, error codes, product names
    - Queries requiring exact word matches
    - Short, specific queries
    
    Args:
        query: The search query text
        top_k: Number of results to return (uses config default if None)
        
    Returns:
        List of matching documents with rank scores
        Format: [{"id": int, "content": str, "metadata": dict, "rank": float, "score": float}]
        
    Raises:
        ValueError: If query is empty
        Exception: If database query fails
    """
    if not query or not query.strip():
        raise ValueError("Query cannot be empty")
    
    config = get_config()
    if top_k is None:
        top_k = config.top_k
    
    client = get_supabase_client()
    
    try:
        response = client.rpc(
            "search_documents_keyword",
            {
                "query_text": query,
                "match_count": top_k
            }
        ).execute()
        
        results = response.data if response.data else []
        
        # Normalize: add 'score' field for consistency with semantic search
        # For keyword search, rank is already the relevance score
        for result in results:
            result["score"] = result.get("rank", 0.0)
        
        return results
        
    except Exception as e:
        raise Exception(f"Failed to search by keywords: {str(e)}")
