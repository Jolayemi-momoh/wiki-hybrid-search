import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

query_text = "space exploration"

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        cur.execute("""
            EXPLAIN ANALYZE
            SELECT id, chunk_text
            FROM article_chunks
            WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery('english', %s);
        """, (query_text,))
        for row in cur.fetchall():
            print(row[0])
