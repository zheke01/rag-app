"""Embeddings module for generating document embeddings."""

from typing import List
import openai


def get_embedding(text: str, model: str) -> List[float]:
    """Generate embedding for text using OpenAI."""
    response = openai.Embedding.create(
        input=text,
        model=model
    )
    return response["data"][0]["embedding"]


def get_embeddings_batch(texts: List[str], model: str) -> List[List[float]]:
    """Generate embeddings for multiple texts."""
    response = openai.Embedding.create(
        input=texts,
        model=model
    )
    return [item["embedding"] for item in response["data"]]
