"""Main entry point for RAG application."""

import click
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.config import get_config
from app.db import get_db_client
from app.ingest import ingest_documents
from app.embeddings import get_embedding
from app.retrieve import retrieve_documents
from app.chat import chat_with_rag


@click.group()
def cli():
    """RAG Application CLI."""
    pass


@cli.command()
@click.argument("file_path", type=click.Path(exists=True))
def ingest(file_path: str):
    """Ingest documents into vector database."""
    try:
        config = get_config()
        db_client = get_db_client(config.supabase_url, config.supabase_key)
        
        click.echo(f"Ingesting documents from: {file_path}")
        total_chunks = ingest_documents(file_path, db_client, config)
        click.echo(f"✓ Successfully ingested {total_chunks} chunks")
        
    except Exception as e:
        click.echo(f"✗ Error during ingestion: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--query", prompt="Enter your question", help="Query for RAG")
def chat(query: str):
    """Chat with RAG system."""
    try:
        config = get_config()
        db_client = get_db_client(config.supabase_url, config.supabase_key)
        
        click.echo("Searching documents...")
        
        # Get embedding for query
        query_embedding = get_embedding(query, config.embedding_model)
        
        # Retrieve similar documents
        documents = retrieve_documents(query_embedding, db_client, config)
        
        # Build context
        context = "\n\n".join([doc.get("content", "") for doc in documents])
        
        click.echo("Generating response...")
        response = chat_with_rag(query, context, config.chat_model)
        
        click.echo(f"\nAnswer:\n{response}")
        
    except Exception as e:
        click.echo(f"✗ Error during chat: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
