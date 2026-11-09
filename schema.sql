-- Enable vector search extensions bundled in Docker
CREATE EXTENSION IF NOT EXISTS vector CASCADE;
CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;

-- Create the base table for Wikipedia articles
CREATE TABLE IF NOT EXISTS articles (
    id TEXT PRIMARY KEY,
    url TEXT,
    title TEXT,
    body TEXT,
    word_count INTEGER
);
