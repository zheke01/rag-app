"""Ingest module for processing and storing documents."""

from typing import List
from pathlib import Path


def load_documents(file_path: str) -> List[str]:
    """Load documents from file."""
    path = Path(file_path)
    
    if path.suffix == ".txt":
        with open(path, "r", encoding="utf-8") as f:
            return [f.read()]
    
    # Add support for other formats as needed
    raise ValueError(f"Unsupported file format: {path.suffix}")


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Split text into chunks."""
    chunks = []
    for i in range(0, len(text), chunk_size - chunk_overlap):
        chunks.append(text[i : i + chunk_size])
    return chunks


def ingest_documents(file_path: str, db_client, config) -> int:
    """Ingest documents into database."""
    documents = load_documents(file_path)
    
    total_chunks = 0
    for doc in documents:
        chunks = chunk_text(doc, config.chunk_size, config.chunk_overlap)
        total_chunks += len(chunks)
        # TODO: Generate embeddings and store in database
    
    return total_chunks
