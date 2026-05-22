-- RPC function for keyword/lexical search using PostgreSQL full-text search
-- This complements semantic search for hybrid search approach

CREATE OR REPLACE FUNCTION search_documents_keyword(
    query_text TEXT,
    match_count INT DEFAULT 5
)
RETURNS TABLE(
    id BIGINT,
    content TEXT,
    metadata JSONB,
    rank FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        ts_rank(documents.content_tsv, websearch_to_tsquery('english', query_text)) AS rank
    FROM documents
    WHERE documents.content_tsv @@ websearch_to_tsquery('english', query_text)
    ORDER BY rank DESC
    LIMIT match_count;
END;
$$ LANGUAGE PLPGSQL;
