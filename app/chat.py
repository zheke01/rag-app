"""Chat module for RAG interactions."""

import openai
from typing import Optional


def chat_with_rag(
    query: str,
    context: str,
    model: str,
    temperature: float = 0.7
) -> str:
    """Generate response using GPT with RAG context."""
    prompt = f"""You are a helpful assistant. Use the provided context to answer the question.

Context:
{context}

Question: {query}

Answer:"""
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature
    )
    
    return response["choices"][0]["message"]["content"]
