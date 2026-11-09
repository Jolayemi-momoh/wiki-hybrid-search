import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

print("Building GIN index on article_chunks (this may take a few seconds)...")
with psycopg.connect(db_url, autocommit=True) as conn:
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_chunks_fts 
        ON article_chunks USING gin (to_tsvector('english', chunk_text));
    """)
print("Success: GIN index created!")
