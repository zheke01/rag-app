"""Main entry point for RAG application."""

import click
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.config import get_config
from app.ingest import ingest_file
from app.chat import answer_question


@click.group()
def cli():
    """RAG Application - Ask questions about your documents."""
    pass


@cli.command()
@click.option("--file", required=True, type=click.Path(exists=True), help="Path to text file to ingest")
def ingest(file: str):
    """Ingest a document into the vector database."""
    try:
        click.echo("=" * 50)
        click.echo("RAG Ingestion")
        click.echo("=" * 50)
        ingest_file(file)
        click.echo("=" * 50)
        click.echo("✓ Ingestion completed successfully!")
        
    except FileNotFoundError as e:
        click.echo(f"✗ File error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"✗ Validation error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Error during ingestion: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option("--debug", is_flag=True, help="Show debug information")
@click.option("--mode", type=click.Choice(["semantic", "keyword", "hybrid"], case_sensitive=False), default="hybrid", help="Search mode (default: hybrid)")
def chat(debug: bool, mode: str):
    """Chat with the RAG system - ask questions about ingested documents.
    
    Search modes:
    - semantic: Vector similarity search (meaning-based)
    - keyword: Full-text search (exact word matching)
    - hybrid: Combined search with RRF fusion (recommended)
    """
    try:
        config = get_config()
        
        click.echo("=" * 50)
        click.echo(f"RAG Chat - {mode.upper()} Search Mode")
        click.echo("=" * 50)
        click.echo("Type 'exit' to quit")
        click.echo("=" * 50)
        
        while True:
            try:
                question = click.prompt("\nYour question")
                
                if question.lower() == "exit":
                    click.echo("Goodbye!")
                    break
                
                if not question.strip():
                    continue
                
                click.echo(f"\nSearching context using {mode} search...")
                answer = answer_question(question, debug=debug, search_mode=mode)
                
                click.echo(f"\nAnswer:\n{answer}")
                
            except ValueError as e:
                click.echo(f"✗ Input error: {e}", err=True)
            except Exception as e:
                click.echo(f"✗ Error: {e}", err=True)
    
    except Exception as e:
        click.echo(f"✗ Fatal error: {e}", err=True)
        sys.exit(1)


@cli.command()
def status():
    """Check configuration and database connection."""
    try:
        config = get_config()
        
        click.echo("Configuration Status:")
        click.echo(f"  OpenAI API Key: {'✓' if config.openai_api_key else '✗'}")
        click.echo(f"  Supabase URL: {'✓' if config.supabase_url else '✗'}")
        click.echo(f"  Supabase Key: {'✓' if config.supabase_key else '✗'}")
        click.echo(f"  Embedding Model: {config.embedding_model}")
        click.echo(f"  Chat Model: {config.chat_model}")
        click.echo(f"  Chunk Size: {config.chunk_size}")
        click.echo(f"  Chunk Overlap: {config.chunk_overlap}")
        click.echo(f"  Top K: {config.top_k}")
        click.echo(f"  Search Mode: {config.search_mode}")
        click.echo(f"  RRF K: {config.rrf_k}")
        
        if not all([config.openai_api_key, config.supabase_url, config.supabase_key]):
            click.echo("\n⚠ Missing configuration - check .env file", err=True)
            sys.exit(1)
        else:
            click.echo("\n✓ All settings configured")
        
    except Exception as e:
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
