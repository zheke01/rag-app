"""Ingest module for processing and storing documents."""

from typing import List
from pathlib import Path
import json
from app.config import get_config
from app.embeddings import embed_texts
from app.db import insert_documents


def _load_text_file(file_path: str) -> str:
    """Load text from a .txt file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        File contents as string
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file is not .txt format
    """
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    if path.suffix.lower() != ".txt":
        raise ValueError(f"Unsupported file format: {path.suffix}. Only .txt files are supported.")
    
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def _chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Split text into overlapping chunks.
    
    Args:
        text: Text to split
        chunk_size: Size of each chunk in characters
        chunk_overlap: Number of overlapping characters between chunks
        
    Returns:
        List of text chunks
    """
    if not text:
        return []
    
    chunks = []
    step = chunk_size - chunk_overlap
    
    for i in range(0, len(text), step):
        chunk = text[i : i + chunk_size]
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk)
    
    return chunks


def ingest_file(file_path: str) -> None:
    """Ingest a text file into the vector database.
    
    Steps:
    1. Load the text file
    2. Split into overlapping chunks
    3. Generate embeddings for each chunk
    4. Store chunks with embeddings in Supabase
    
    Args:
        file_path: Path to the text file to ingest
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is unsupported or has no content
        Exception: If embedding or database operations fail
    """
    config = get_config()
    
    # Validate inputs
    if not config.openai_api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")
    if not config.supabase_url or not config.supabase_key:
        raise ValueError("Supabase credentials not set in environment")
    
    # Load file
    print(f"Loading file: {file_path}")
    text = _load_text_file(file_path)
    
    if not text or not text.strip():
        raise ValueError("File is empty")
    
    file_name = Path(file_path).name
    
    # Chunk text
    print(f"Chunking text (size={config.chunk_size}, overlap={config.chunk_overlap})...")
    chunks = _chunk_text(text, config.chunk_size, config.chunk_overlap)
    
    if not chunks:
        raise ValueError("No chunks created from file")
    
    print(f"Created {len(chunks)} chunks")
    
    # Generate embeddings
    print("Generating embeddings...")
    embeddings = embed_texts(chunks)
    
    if len(embeddings) != len(chunks):
        raise Exception(f"Embedding count mismatch: got {len(embeddings)}, expected {len(chunks)}")
    
    # Prepare rows for insertion
    rows = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        rows.append({
            "content": chunk,
            "embedding": embedding,
            "metadata": json.dumps({
                "source": file_name,
                "chunk_index": idx
            })
        })
    
    # Insert into database
    print("Inserting into database...")
    inserted = insert_documents(rows)
    
    print(f"✓ Successfully ingested {inserted} chunks from {file_name}")
