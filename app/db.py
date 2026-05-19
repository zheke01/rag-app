"""Database module for Supabase connection."""

from typing import Optional
from supabase import create_client, Client
from app.config import get_config


_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get or create Supabase client singleton."""
    global _client
    
    if _client is None:
        config = get_config()
        _client = create_client(config.supabase_url, config.supabase_key)
    
    return _client


def insert_documents(rows: list[dict]) -> int:
    """Insert document chunks into the documents table.
    
    Args:
        rows: List of dicts with keys: content, embedding, metadata
        
    Returns:
        Number of inserted rows
    """
    if not rows:
        return 0
    
    client = get_supabase_client()
    
    try:
        response = client.table("documents").insert(rows).execute()
        return len(response.data) if response.data else 0
    except Exception as e:
        raise Exception(f"Failed to insert documents: {str(e)}")


def match_documents(query_embedding: list[float], top_k: int) -> list[dict]:
    """Call match_documents RPC function to retrieve similar documents.
    
    Args:
        query_embedding: Query vector (1536 dimensions)
        top_k: Number of results to return
        
    Returns:
        List of matching documents with similarity scores
    """
    client = get_supabase_client()
    
    try:
        response = client.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_count": top_k
            }
        ).execute()
        
        return response.data if response.data else []
    except Exception as e:
        raise Exception(f"Failed to match documents: {str(e)}")
