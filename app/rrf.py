"""Reciprocal Rank Fusion (RRF) algorithm for combining search results."""

from typing import List, Dict


def reciprocal_rank_fusion(
    results_list: List[List[Dict]],
    k: int = 60
) -> List[Dict]:
    """Combine multiple ranked lists using Reciprocal Rank Fusion.
    
    RRF is a simple yet effective method to combine rankings from different
    retrieval strategies. Each document gets a score based on its rank position
    in each list, using the formula: score = 1 / (rank + k)
    
    The constant k (typically 60) prevents top-ranked items from dominating
    and gives fair weight to items that appear in multiple lists.
    
    Example:
        If a document is rank 1 in semantic search and rank 3 in keyword search:
        - Semantic contribution: 1/(1+60) = 0.0164
        - Keyword contribution: 1/(3+60) = 0.0159
        - Total RRF score: 0.0323
    
    Args:
        results_list: List of result lists from different search methods.
                     Each result should have an 'id' field.
                     Example: [semantic_results, keyword_results]
        k: RRF constant (default 60, as commonly used in literature)
        
    Returns:
        Combined and re-ranked list of documents sorted by RRF score (highest first).
        Each document includes its original data plus 'rrf_score' field.
        
    Raises:
        ValueError: If results_list is empty or contains invalid data
    """
    if not results_list:
        raise ValueError("results_list cannot be empty")
    
    # Dictionary to accumulate scores: {doc_id: {"score": float, "doc": dict}}
    fused_scores = {}
    
    # Process each ranked list
    for result_list in results_list:
        if not result_list:
            continue  # Skip empty lists
            
        for rank, doc in enumerate(result_list):
            doc_id = doc.get("id")
            
            if doc_id is None:
                continue  # Skip documents without ID
            
            # Calculate RRF score contribution from this list
            # rank starts at 0, so rank 0 gets highest score: 1/(0+60)
            rrf_contribution = 1.0 / (rank + k)
            
            if doc_id not in fused_scores:
                fused_scores[doc_id] = {
                    "score": 0.0,
                    "doc": doc  # Keep the document data
                }
            
            # Accumulate score from this ranking
            fused_scores[doc_id]["score"] += rrf_contribution
    
    if not fused_scores:
        return []  # No valid results found
    
    # Sort by RRF score (highest first) and prepare output
    sorted_results = sorted(
        fused_scores.items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )
    
    # Format output: add rrf_score to each document
    final_results = []
    for doc_id, data in sorted_results:
        doc = data["doc"].copy()
        doc["rrf_score"] = data["score"]
        final_results.append(doc)
    
    return final_results


def explain_rrf_ranking(
    semantic_results: List[Dict],
    keyword_results: List[Dict],
    fused_results: List[Dict],
    top_n: int = 3
) -> str:
    """Generate human-readable explanation of RRF ranking process.
    
    Useful for debugging and understanding why documents were ranked
    in a particular order.
    
    Args:
        semantic_results: Results from semantic/vector search
        keyword_results: Results from keyword search
        fused_results: Results after RRF fusion
        top_n: Number of top results to explain
        
    Returns:
        Formatted string explaining the ranking
    """
    explanation = ["=== RRF Ranking Explanation ===\n"]
    
    # Create lookup maps for original rankings
    semantic_ranks = {doc["id"]: i for i, doc in enumerate(semantic_results)}
    keyword_ranks = {doc["id"]: i for i, doc in enumerate(keyword_results)}
    
    explanation.append(f"Top {top_n} results after RRF fusion:\n")
    
    for i, doc in enumerate(fused_results[:top_n], 1):
        doc_id = doc["id"]
        rrf_score = doc.get("rrf_score", 0)
        content_preview = doc.get("content", "")[:80] + "..."
        
        sem_rank = semantic_ranks.get(doc_id)
        kw_rank = keyword_ranks.get(doc_id)
        
        explanation.append(f"\n#{i} - Document ID: {doc_id}")
        explanation.append(f"   RRF Score: {rrf_score:.4f}")
        explanation.append(f"   Content: {content_preview}")
        explanation.append(f"   Rankings:")
        
        if sem_rank is not None:
            sem_contrib = 1.0 / (sem_rank + 60)
            explanation.append(f"     - Semantic Search: Rank {sem_rank + 1} (score contribution: {sem_contrib:.4f})")
        else:
            explanation.append(f"     - Semantic Search: Not found")
        
        if kw_rank is not None:
            kw_contrib = 1.0 / (kw_rank + 60)
            explanation.append(f"     - Keyword Search: Rank {kw_rank + 1} (score contribution: {kw_contrib:.4f})")
        else:
            explanation.append(f"     - Keyword Search: Not found")
    
    return "\n".join(explanation)
