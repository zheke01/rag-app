"""Hybrid search module combining semantic and keyword search with RRF."""

from typing import List, Dict, Literal
from app.config import get_config
from app.embeddings import embed_text
from app.db import match_documents
from app.keyword_search import search_by_keywords
from app.rrf import reciprocal_rank_fusion, explain_rrf_ranking


SearchMode = Literal["semantic", "keyword", "hybrid"]


def hybrid_retrieve_context(
    question: str,
    mode: SearchMode = "hybrid",
    top_k: int = None,
    rrf_k: int = 60,
    debug: bool = False
) -> tuple[List[Dict], str]:
    """Retrieve relevant documents using hybrid search (semantic + keyword + RRF).
    
    This function combines:
    1. Semantic search (vector similarity) - good for understanding meaning/context
    2. Keyword search (full-text search) - good for exact terms, names, codes
    3. RRF fusion - intelligently combines both rankings
    
    Args:
        question: The user's question
        mode: Search mode - "semantic", "keyword", or "hybrid"
        top_k: Number of results to retrieve from each search method
        rrf_k: RRF constant (default 60)
        debug: If True, return detailed ranking explanation
        
    Returns:
        Tuple of (results, explanation)
        - results: List of relevant document chunks
        - explanation: Debug info (empty string if debug=False)
        
    Raises:
        ValueError: If question is empty or mode is invalid
        Exception: If search operations fail
    """
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")
    
    if mode not in ["semantic", "keyword", "hybrid"]:
        raise ValueError(f"Invalid mode: {mode}. Must be 'semantic', 'keyword', or 'hybrid'")
    
    config = get_config()
    if top_k is None:
        top_k = config.top_k
    
    explanation = ""
    
    try:
        # Mode 1: Semantic search only
        if mode == "semantic":
            question_embedding = embed_text(question)
            results = match_documents(question_embedding, top_k)
            
            if debug:
                explanation = f"=== SEMANTIC SEARCH ONLY ===\nRetrieved {len(results)} documents using vector similarity.\n"
            
            return results, explanation
        
        # Mode 2: Keyword search only
        elif mode == "keyword":
            results = search_by_keywords(question, top_k)
            
            if debug:
                explanation = f"=== KEYWORD SEARCH ONLY ===\nRetrieved {len(results)} documents using full-text search.\n"
            
            return results, explanation
        
        # Mode 3: Hybrid search with RRF
        else:  # mode == "hybrid"
            # Run both searches in parallel conceptually
            question_embedding = embed_text(question)
            semantic_results = match_documents(question_embedding, top_k)
            keyword_results = search_by_keywords(question, top_k)
            
            # Combine using RRF
            fused_results = reciprocal_rank_fusion(
                [semantic_results, keyword_results],
                k=rrf_k
            )
            
            # Take top_k from fused results
            final_results = fused_results[:top_k]
            
            if debug:
                explanation = f"=== HYBRID SEARCH (RRF) ===\n"
                explanation += f"Semantic search: {len(semantic_results)} results\n"
                explanation += f"Keyword search: {len(keyword_results)} results\n"
                explanation += f"Fused results: {len(fused_results)} total\n"
                explanation += f"Returning top {len(final_results)}\n\n"
                explanation += explain_rrf_ranking(
                    semantic_results,
                    keyword_results,
                    fused_results,
                    top_n=min(5, len(final_results))
                )
            
            return final_results, explanation
            
    except Exception as e:
        raise Exception(f"Failed to retrieve context: {str(e)}")


def retrieve_context_semantic_only(question: str) -> List[Dict]:
    """Retrieve context using semantic search only (backward compatibility).
    
    This maintains compatibility with existing code that uses simple semantic search.
    
    Args:
        question: The user's question
        
    Returns:
        List of relevant document chunks
    """
    results, _ = hybrid_retrieve_context(question, mode="semantic", debug=False)
    return results


def retrieve_context_keyword_only(question: str) -> List[Dict]:
    """Retrieve context using keyword search only.
    
    Args:
        question: The user's question
        
    Returns:
        List of relevant document chunks
    """
    results, _ = hybrid_retrieve_context(question, mode="keyword", debug=False)
    return results


def retrieve_context_hybrid(question: str, debug: bool = False) -> tuple[List[Dict], str]:
    """Retrieve context using hybrid search (default).
    
    Args:
        question: The user's question
        debug: If True, return detailed ranking explanation
        
    Returns:
        Tuple of (results, explanation)
    """
    return hybrid_retrieve_context(question, mode="hybrid", debug=debug)
