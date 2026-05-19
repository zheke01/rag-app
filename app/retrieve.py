"""Retrieval module for searching documents."""

from typing import List, Dict
from app.config import get_config
from app.embeddings import embed_text
from app.db import match_documents


def retrieve_context(question: str) -> List[Dict]:
    """Retrieve relevant documents for a question.
    
    Process:
    1. Generate embedding for the question
    2. Call match_documents RPC to find similar chunks
    3. Return the most relevant chunks
    
    Args:
        question: The user's question
        
    Returns:
        List of relevant document chunks with metadata and similarity scores
        
    Raises:
        ValueError: If question is empty or embedding fails
        Exception: If database query fails
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    config = get_config()
    
    try:
        # Generate embedding for question
        question_embedding = embed_text(question)
        
        # Retrieve similar documents
        results = match_documents(question_embedding, config.top_k)
        
        return results
    except Exception as e:
        raise Exception(f"Failed to retrieve context: {str(e)}")
