-- Add full-text search support for keyword/lexical search
-- This enables hybrid search combining semantic (vector) and keyword search

-- Add tsvector column for full-text search
ALTER TABLE documents
ADD COLUMN IF NOT EXISTS content_tsv tsvector;

-- Populate tsvector column with existing data
UPDATE documents
SET content_tsv = to_tsvector('english', content)
WHERE content_tsv IS NULL;

-- Create GIN index on tsvector column for fast keyword search
CREATE INDEX IF NOT EXISTS documents_content_tsv_idx
ON documents USING gin(content_tsv);

-- Create trigger to automatically update tsvector when content changes
CREATE OR REPLACE FUNCTION documents_content_tsv_trigger() RETURNS trigger AS $$
BEGIN
    NEW.content_tsv := to_tsvector('english', NEW.content);
    RETURN NEW;
END
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS documents_content_tsv_update ON documents;

CREATE TRIGGER documents_content_tsv_update
BEFORE INSERT OR UPDATE ON documents
FOR EACH ROW
EXECUTE FUNCTION documents_content_tsv_trigger();
