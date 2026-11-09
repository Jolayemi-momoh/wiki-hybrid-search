-- Create table for storing article text chunks and embeddings
CREATE TABLE IF NOT EXISTS article_chunks (
    id SERIAL PRIMARY KEY,
    article_id TEXT REFERENCES articles(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    chunk_text TEXT,
    embedding VECTOR(384)
);

-- Create HNSW index for fast vector cosine similarity search
CREATE INDEX IF NOT EXISTS idx_chunks_embedding 
ON article_chunks USING hnsw (embedding vector_cosine_ops);
