"""Database module for Supabase connection."""

from typing import Optional
from postgrest import AsyncpostgrestClient
from supabase import create_client, Client


def get_db_client(url: str, key: str) -> Client:
    """Create and return Supabase client."""
    client = create_client(url, key)
    return client
