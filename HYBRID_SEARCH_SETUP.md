# Hybrid Search Setup Guide

This guide walks you through setting up and testing the hybrid search feature with RRF (Reciprocal Rank Fusion).

## Overview

The hybrid search combines two retrieval methods:
1. **Semantic Search** (Vector similarity) - Understands meaning and context
2. **Keyword Search** (Full-text search) - Finds exact word matches
3. **RRF Fusion** - Intelligently combines both rankings

## Prerequisites

- Supabase account and project
- OpenAI API key
- Python 3.8+
- Existing documents ingested into the database

## Setup Steps

### Step 1: Update Database Schema

Run the following SQL scripts in your Supabase SQL Editor (in order):

#### 1.1 Add Full-Text Search Support
```sql
-- File: sql/add_fulltext_search.sql
-- This adds tsvector column and index for keyword search
```

Open your Supabase project → SQL Editor → Run `sql/add_fulltext_search.sql`

#### 1.2 Create Keyword Search Function
```sql
-- File: sql/search_documents_keyword.sql
-- This creates the RPC function for keyword search
```

Run `sql/search_documents_keyword.sql` in SQL Editor

### Step 2: Verify Database Setup

Check that the following were created:
- Column: `documents.content_tsv` (tsvector)
- Index: `documents_content_tsv_idx` (GIN index)
- Function: `search_documents_keyword(text, int)`
- Trigger: `documents_content_tsv_update`

You can verify with:
```sql
-- Check column exists
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'documents' AND column_name = 'content_tsv';

-- Check function exists
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_name = 'search_documents_keyword';
```

### Step 3: Update Configuration

Your `.env` file should include:
```env
# Existing settings
OPENAI_API_KEY=sk-...
SUPABASE_URL=https://...supabase.co
SUPABASE_KEY=eyJ...

# New hybrid search settings
SEARCH_MODE=hybrid  # Options: semantic, keyword, hybrid
RRF_K=60  # RRF constant (typically 60)
```

### Step 4: Test the Setup

#### Option A: Run Test Script
```bash
python test_hybrid_search.py
```

This will run comparison tests showing how each search mode performs.

#### Option B: Interactive Chat
```bash
# Hybrid search (default)
python -m app.main chat --mode hybrid --debug

# Semantic only
python -m app.main chat --mode semantic --debug

# Keyword only
python -m app.main chat --mode keyword --debug
```

## Understanding the Results

### Semantic Search
- Best for: Conceptual questions, understanding meaning
- Example: "How do I improve performance?" → finds docs about optimization
- Score metric: `similarity` (0.0 to 1.0, higher is better)

### Keyword Search
- Best for: Exact terms, error codes, product names
- Example: "error 404" → finds exact mentions of "404"
- Score metric: `rank` (higher is better, based on term frequency)

### Hybrid Search (RRF)
- Best for: General queries that benefit from both approaches
- Combines both methods using Reciprocal Rank Fusion
- Score metric: `rrf_score` (sum of 1/(rank+60) from each method)

### RRF Formula
```
For each document:
  rrf_score = 1/(semantic_rank + 60) + 1/(keyword_rank + 60)
  
Example:
  Doc appears at rank 1 in semantic, rank 3 in keyword:
  rrf_score = 1/(1+60) + 1/(3+60) = 0.0164 + 0.0159 = 0.0323
```

## Test Scenarios

### Scenario 1: Technical Error Code
**Query:** "error 404 not found"
- **Semantic:** May find general error handling docs
- **Keyword:** Will find exact "404" mentions (better)
- **Hybrid:** Balances both, prioritizes exact matches

### Scenario 2: Conceptual Question
**Query:** "How can I improve application performance?"
- **Semantic:** Finds optimization, caching, performance docs (better)
- **Keyword:** May miss if exact words don't match
- **Hybrid:** Primarily uses semantic, boosted by keyword overlap

### Scenario 3: Mixed Query
**Query:** "PostgreSQL connection timeout"
- **Semantic:** Understands it's about database connectivity issues
- **Keyword:** Finds exact mentions of "PostgreSQL" and "timeout"
- **Hybrid:** Best of both - exact product name + conceptual understanding

## Troubleshooting

### Issue: "RPC function not found"
**Solution:** Run `sql/search_documents_keyword.sql` in Supabase SQL Editor

### Issue: Keyword search returns no results
**Solution:** 
1. Check if `content_tsv` column is populated:
   ```sql
   SELECT COUNT(*) FROM documents WHERE content_tsv IS NOT NULL;
   ```
2. If empty, run:
   ```sql
   UPDATE documents SET content_tsv = to_tsvector('english', content);
   ```

### Issue: "column content_tsv does not exist"
**Solution:** Run `sql/add_fulltext_search.sql` in Supabase SQL Editor

### Issue: Poor hybrid results
**Solution:** 
1. Try adjusting `RRF_K` in `.env` (lower = more emphasis on top ranks)
2. Adjust `TOP_K` to retrieve more candidates
3. Check if your documents are well-distributed between both search types

## Performance Notes

- **Semantic Search:** Slightly slower (vector comparison), very accurate for meaning
- **Keyword Search:** Very fast (GIN index), great for exact matches
- **Hybrid Search:** 2x searches + fusion, but provides best overall results

## Example Output

When running with `--debug`, you'll see:

```
=== HYBRID SEARCH (RRF) ===
Semantic search: 5 results
Keyword search: 5 results
Fused results: 8 total
Returning top 5

=== RRF Ranking Explanation ===

Top 5 results after RRF fusion:

#1 - Document ID: 42
   RRF Score: 0.0323
   Content: PostgreSQL connection timeout errors can occur when...
   Rankings:
     - Semantic Search: Rank 1 (score contribution: 0.0164)
     - Keyword Search: Rank 3 (score contribution: 0.0159)
```

## Next Steps

1. ✅ Test with your specific documents
2. ✅ Compare all three modes to see the difference
3. ✅ Document your findings for the assignment deliverable
4. ✅ Create screenshots showing the comparison
5. ✅ Push changes to your repository

## Resources

- [PostgreSQL Full-Text Search](https://www.postgresql.org/docs/current/textsearch.html)
- [RRF Paper](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
- [Supabase Documentation](https://supabase.com/docs)
