import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

with psycopg.connect(db_url, autocommit=True) as conn:
    with open("update_schema.sql", "r") as file:
        conn.execute(file.read())
    print("Success: Created article_chunks table and HNSW vector index!")
