import os 
import psycopg
from dotenv import load_dotenv
from datasets import load_dataset

load_dotenv()
db_url =os.getenv("DATABASE_URL")

print("Fetching wikipedia dataset stream from Hugging Face...")
ds = load_dataset("wikimedia/wikipedia", "20231101.simple",split="train", streaming=True)
print ("connecting to PostgreSQL and ingesting articles.....")
batch_size=500
limit =5000
batch=[]
count = 0

insert_query= """ INSERT INTO articles (id, url,title, body, word_count)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (id) DO NOTHING;
"""

with psycopg.connect(db_url) as conn:
    with conn.cursor() as cur:
        for item in ds:
            article_id = str(item.get("id"))
            url = item.get("url", "")
            title=item.get("title", "")
            body = item.get("text", "")
            word_count = len(body.split())

            batch.append((article_id, url, title, body, word_count))
            count += 1

            if len(batch) >= batch_size:
                cur.executemany(insert_query, batch)
                conn.commit()
                print(f"Loaded {count}/{limit} articles...")
                batch = []

            if count >= limit:
                break

        if batch:
            cur.executemany(insert_query, batch)
            conn.commit()

print(f"Finished! Successfully populated 'articles' table with {count} records.")
