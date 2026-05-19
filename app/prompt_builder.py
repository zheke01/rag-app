"""Prompt builder module for constructing LLM prompts."""

from typing import List, Dict


def build_context(documents: List[Dict]) -> str:
    """Build context string from retrieved documents."""
    if not documents:
        return ""
    
    context_parts = []
    for doc in documents:
        context_parts.append(doc.get("content", ""))
    
    return "\n\n".join(context_parts)


def build_prompt(query: str, context: str) -> str:
    """Build complete prompt for LLM."""
    prompt = f"""You are a helpful assistant. Use the provided context to answer the question.

Context:
{context}

Question: {query}

Answer:"""
    return prompt
