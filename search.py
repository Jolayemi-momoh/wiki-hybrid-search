import sys
import os
import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
db_url = os.getenv("DATABASE_URL")
device = os.getenv("MODEL_DEVICE", "cpu")

print("Loading model...")
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

def hybrid_search(query_text, top_k=5):
    # 1. Convert search phrase into dense vector array
    query_vector = model.encode(query_text).tolist()

    # 2. Combine FTS + Vector RRF in PostgreSQL
    sql = """
    WITH fts_search AS (
        SELECT id, article_id, chunk_text,
               ROW_NUMBER() OVER (ORDER BY ts_rank(to_tsvector('english', chunk_text), plainto_tsquery('english', %s)) DESC) as fts_rank
        FROM article_chunks
        WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery('english', %s)
        LIMIT 60
    ),
    vector_search AS (
        SELECT id, article_id, chunk_text,
               ROW_NUMBER() OVER (ORDER BY embedding <=> %s::vector) as vector_rank
        FROM article_chunks
        ORDER BY embedding <=> %s::vector
        LIMIT 60
    )
    SELECT
        COALESCE(f.article_id, v.article_id) as article_id,
        a.title,
        COALESCE(f.chunk_text, v.chunk_text) as chunk_text,
        COALESCE(1.0 / (60 + f.fts_rank), 0.0) + COALESCE(1.0 / (60 + v.vector_rank), 0.0) as rrf_score
    FROM fts_search f
    FULL OUTER JOIN vector_search v ON f.id = v.id
    JOIN articles a ON a.id = COALESCE(f.article_id, v.article_id)
    ORDER BY rrf_score DESC
    LIMIT %s;
    """

    with psycopg.connect(db_url) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (query_text, query_text, str(query_vector), str(query_vector), top_k))
            return cur.fetchall()

if __name__ == "__main__":
    query = sys.argv[1] if len(sys.argv) > 1 else "Albert Einstein general relativity"
    print(f"\n=== Hybrid Search Results for: '{query}' ===")
    results = hybrid_search(query)
    for i, (art_id, title, snippet, score) in enumerate(results, 1):
        clean_snippet = snippet.replace('\n', ' ').strip()
        print(f"\n{i}. [{title}] (RRF Score: {score:.4f})")
        print(f"   Snippet: {clean_snippet[:200]}...")
