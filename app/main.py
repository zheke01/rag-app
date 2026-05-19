"""Main entry point for RAG application."""

import click
import sys
import os
import json

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.config import get_config
from app.ingest import ingest_file
from app.retrieve import retrieve_context
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
        click.echo(f"Starting ingestion: {file_path}")
        ingest_file(file_path)
        
    except Exception as e:
        click.echo(f"✗ Error during ingestion: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--query", prompt="Enter your question", help="Query for RAG")
def chat(query: str):
    """Chat with RAG system."""
    try:
        config = get_config()
        
        click.echo("Searching documents...")
        documents = retrieve_context(query)
        
        if not documents:
            click.echo("No relevant documents found.")
            return
        
        click.echo(f"Found {len(documents)} relevant chunks")
        
        # Build context from retrieved documents
        context_parts = []
        for i, doc in enumerate(documents, 1):
            similarity = doc.get("similarity", 0)
            content = doc.get("content", "")
            context_parts.append(f"[{i}] (similarity: {similarity:.2f})\n{content[:200]}...")
        
        context = "\n\n".join(context_parts)
        
        click.echo("\nGenerating response...")
        response = chat_with_rag(query, context, config.chat_model)
        
        click.echo(f"\nAnswer:\n{response}")
        
    except Exception as e:
        click.echo(f"✗ Error during chat: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
