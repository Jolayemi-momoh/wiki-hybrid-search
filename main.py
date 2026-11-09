import os
from typing import List
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

load_dotenv()
db_url = os.getenv("DATABASE_URL")
device = os.getenv("MODEL_DEVICE", "cpu")

app = FastAPI(
    title="Local Wikipedia Hybrid Search API",
    description="FastAPI service combining BM25 keyword search and pgvector semantic search using RRF."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading SentenceTransformer model...")
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

class SearchResult(BaseModel):
    article_id: str
    title: str
    chunk_text: str
    rrf_score: float

@app.get("/")
def serve_ui():
    return FileResponse("index.html")

@app.get("/search", response_model=List[SearchResult])
def search(
    q: str = Query(..., description="Query string to search Wikipedia chunks"),
    limit: int = Query(5, ge=1, le=50, description="Number of results to return")
):
    query_vector = model.encode(q).tolist()

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
            cur.execute(sql, (q, q, str(query_vector), str(query_vector), limit))
            rows = cur.fetchall()

    return [
        SearchResult(
            article_id=row[0],
            title=row[1],
            chunk_text=row[2],
            rrf_score=float(row[3])
        )
        for row in rows
    ]

@app.get("/health")
def health_check():
    return {"status": "ok", "database": "connected"}
