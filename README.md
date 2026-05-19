
# RAG Application - Retrieval Augmented Generation

A minimal Python RAG application that allows you to upload documents, convert them to embeddings, and ask questions about them.

## Setup

### 1. Create virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

You'll need:
- **OPENAI_API_KEY**: Get from https://platform.openai.com/api-keys
- **SUPABASE_URL**: Project URL from Supabase dashboard
- **SUPABASE_KEY**: Anon public key from Supabase dashboard

### 4. Initialize Supabase database

1. Create a project in [Supabase](https://supabase.com)
2. Open SQL Editor
3. Run `sql/init.sql` to create the documents table
4. Run `sql/match_documents.sql` to create the search function

## Usage

### Check configuration

```bash
python -m app.main status
```

### Ingest documents

```bash
python -m app.main ingest --file data/test.txt
```

This will:
- Load the text file
- Split it into chunks with overlap
- Generate embeddings using OpenAI
- Store chunks with embeddings in Supabase

### Chat with documents

```bash
python -m app.main chat
```

Enter your questions. The system will:
- Generate embedding for your question
- Search for similar document chunks
- Use the relevant chunks as context
- Generate an answer using GPT

Type `exit` to quit.

### Debug mode

To see which chunks were retrieved:

```bash
python -m app.main chat --debug
```

## Architecture

- **app/config.py**: Environment configuration
- **app/db.py**: Supabase database operations
- **app/embeddings.py**: OpenAI embedding generation
- **app/ingest.py**: Document loading, chunking, and ingestion
- **app/retrieve.py**: Vector similarity search
- **app/prompt_builder.py**: LLM prompt construction
- **app/chat.py**: Question answering logic
- **app/main.py**: CLI interface
- **sql/init.sql**: Database initialization
- **sql/match_documents.sql**: Vector similarity RPC function

## Configuration

See `.env.example` for all available options:

```env
# OpenAI
OPENAI_API_KEY=sk-...
EMBEDDING_MODEL=text-embedding-3-small
CHAT_MODEL=gpt-4o-mini

# Supabase
SUPABASE_URL=https://...supabase.co
SUPABASE_KEY=eyJ...

# Chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K=5
```

## Example

```bash
# 1. Add your document
python -m app.main ingest --file data/test.txt

# 2. Ask questions
python -m app.main chat

# Example questions:
# - What is Supabase?
# - How do I get started with Supabase?
# - Explain pgvector
```

## Troubleshooting

**"OPENAI_API_KEY not set"**
- Make sure .env file exists and OPENAI_API_KEY is set
- Run `python -m app.main status` to check

**"Failed to connect to Supabase"**
- Verify SUPABASE_URL and SUPABASE_KEY in .env
- Check that your Supabase project is running

**"No embedding model found"**
- Verify EMBEDDING_MODEL is set in .env
- Default is "text-embedding-3-small"

**"RPC function not found"**
- Make sure you ran sql/match_documents.sql in your Supabase SQL Editor
