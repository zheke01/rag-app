"""Test script for hybrid search functionality.

This script demonstrates the difference between semantic, keyword, and hybrid search
by running comparison queries and showing which documents are retrieved by each method.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from app.hybrid_search import hybrid_retrieve_context
from app.config import get_config


def print_separator(char="=", length=70):
    """Print a separator line."""
    print(char * length)


def print_results(results, search_type):
    """Print search results in a formatted way."""
    print(f"\n{search_type} Results: {len(results)} documents found")
    print_separator("-")
    
    for i, doc in enumerate(results, 1):
        print(f"\n[{i}] ID: {doc.get('id')}")
        
        # Show different scores based on what's available
        if 'rrf_score' in doc:
            print(f"    RRF Score: {doc['rrf_score']:.4f}")
        if 'similarity' in doc:
            print(f"    Similarity: {doc['similarity']:.2%}")
        if 'rank' in doc:
            print(f"    Rank: {doc['rank']:.4f}")
        
        content = doc.get('content', '')
        preview = content[:150] + "..." if len(content) > 150 else content
        print(f"    Content: {preview}")


def test_query(query: str, description: str):
    """Test a query with all three search modes."""
    print_separator("=")
    print(f"TEST: {description}")
    print_separator("=")
    print(f"Query: \"{query}\"")
    print()
    
    try:
        # Semantic Search
        print_separator()
        print("1️⃣  SEMANTIC SEARCH (Vector Similarity)")
        print_separator()
        semantic_results, _ = hybrid_retrieve_context(query, mode="semantic", top_k=5)
        print_results(semantic_results, "Semantic")
        
        # Keyword Search
        print_separator()
        print("2️⃣  KEYWORD SEARCH (Full-Text)")
        print_separator()
        keyword_results, _ = hybrid_retrieve_context(query, mode="keyword", top_k=5)
        print_results(keyword_results, "Keyword")
        
        # Hybrid Search with RRF
        print_separator()
        print("3️⃣  HYBRID SEARCH (RRF Fusion)")
        print_separator()
        hybrid_results, explanation = hybrid_retrieve_context(query, mode="hybrid", top_k=5, debug=True)
        print(f"\n{explanation}")
        
        # Summary
        print_separator()
        print("SUMMARY")
        print_separator()
        print(f"Semantic found: {len(semantic_results)} documents")
        print(f"Keyword found: {len(keyword_results)} documents")
        print(f"Hybrid found: {len(hybrid_results)} documents")
        
        # Check for unique documents in each method
        semantic_ids = {doc['id'] for doc in semantic_results}
        keyword_ids = {doc['id'] for doc in keyword_results}
        hybrid_ids = {doc['id'] for doc in hybrid_results}
        
        only_semantic = semantic_ids - keyword_ids
        only_keyword = keyword_ids - semantic_ids
        in_both = semantic_ids & keyword_ids
        
        print(f"\nDocuments only in semantic: {len(only_semantic)}")
        print(f"Documents only in keyword: {len(only_keyword)}")
        print(f"Documents in both: {len(in_both)}")
        print(f"Total unique in hybrid: {len(hybrid_ids)}")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" * 2)


def main():
    """Run hybrid search tests."""
    print_separator("=")
    print("HYBRID SEARCH TEST SUITE")
    print_separator("=")
    print()
    
    try:
        config = get_config()
        
        # Check configuration
        if not all([config.openai_api_key, config.supabase_url, config.supabase_key]):
            print("❌ Missing configuration. Please set up your .env file.")
            print("Required: OPENAI_API_KEY, SUPABASE_URL, SUPABASE_KEY")
            sys.exit(1)
        
        print("✅ Configuration loaded successfully")
        print(f"   Search Mode: {config.search_mode}")
        print(f"   RRF K: {config.rrf_k}")
        print(f"   Top K: {config.top_k}")
        print()
        
        # Test queries
        test_cases = [
            {
                "query": "error 404 not found",
                "description": "Technical Error Code (Should favor keyword search for exact match)"
            },
            {
                "query": "How can I improve performance?",
                "description": "Conceptual Question (Should favor semantic search for meaning)"
            },
            {
                "query": "database connection timeout",
                "description": "Mixed Technical Terms (Hybrid should combine both approaches)"
            },
            {
                "query": "PostgreSQL pgvector",
                "description": "Specific Product Names (Keyword search should excel here)"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"TEST CASE {i}/{len(test_cases)}")
            print(f"{'='*70}\n")
            test_query(test_case["query"], test_case["description"])
            
            if i < len(test_cases):
                input("Press Enter to continue to next test case...")
        
        print_separator("=")
        print("✅ ALL TESTS COMPLETED")
        print_separator("=")
        print("\nNext Steps:")
        print("1. Review the results above to see how each search mode performs")
        print("2. Try the interactive chat with: python -m app.main chat --mode hybrid --debug")
        print("3. Compare different modes: --mode semantic, --mode keyword, --mode hybrid")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
