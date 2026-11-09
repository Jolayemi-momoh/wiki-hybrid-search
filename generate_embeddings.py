import os
import psycopg
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

load_dotenv()
db_url = os.getenv("DATABASE_URL")
device = os.getenv("MODEL_DEVICE", "cpu")

print("Loading embedding model (all-MiniLM-L6-v2)...")
model = SentenceTransformer("all-MiniLM-L6-v2", device=device)

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

print("Connecting to database and processing articles...")
with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, body FROM articles;")
        articles = cur.fetchall()
        print(f"Found {len(articles)} articles to process.")

        batch = []
        batch_size = 250
        processed = 0

        for article_id, body in articles:
            if not body or len(body.strip()) == 0:
                continue
                
            chunks = chunk_text(body)
            embeddings = model.encode(chunks, show_progress_bar=False)

            for idx, (chunk, emb) in enumerate(zip(chunks, embeddings)):
                batch.append((article_id, idx, chunk, emb.tolist()))

            processed += 1
            if len(batch) >= batch_size:
                cur.executemany(
                    "INSERT INTO article_chunks (article_id, chunk_index, chunk_text, embedding) VALUES (%s, %s, %s, %s);",
                    batch
                )
                conn.commit()
                print(f"Processed {processed}/{len(articles)} articles...")
                batch = []

        if batch:
            cur.executemany(
                "INSERT INTO article_chunks (article_id, chunk_index, chunk_text, embedding) VALUES (%s, %s, %s, %s);",
                batch
            )
            conn.commit()

print("Success: All articles chunked and vectorized!")
