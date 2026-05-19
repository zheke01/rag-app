"""Prompt builder module for constructing LLM prompts."""

from typing import List, Dict


def build_prompt(question: str, contexts: List[Dict]) -> str:
    """Build a complete prompt for LLM with RAG context.
    
    Args:
        question: The user's question
        contexts: List of context documents with 'content' and 'similarity' keys
        
    Returns:
        Complete prompt string
    """
    if not contexts:
        context_text = "No relevant context found."
    else:
        context_blocks = []
        for i, ctx in enumerate(contexts, 1):
            content = ctx.get("content", "").strip()
            similarity = ctx.get("similarity", 0)
            metadata = ctx.get("metadata", {})
            
            block = f"[Context {i}] (Relevance: {similarity:.2%})\n{content}"
            if metadata:
                block += f"\nSource: {metadata}"
            
            context_blocks.append(block)
        
        context_text = "\n\n".join(context_blocks)
    
    prompt = f"""You are a helpful assistant. Your task is to answer the user's question based ONLY on the provided context.

Important Rules:
1. Answer ONLY using information from the context below
2. If the context does not contain information to answer the question, clearly state: "I cannot answer this question based on the provided context."
3. Do not use external knowledge or make assumptions
4. Be concise and direct

Context:
{context_text}

Question: {question}

Answer:"""
    
    return prompt
