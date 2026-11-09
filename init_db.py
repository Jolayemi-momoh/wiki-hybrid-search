import os
import psycopg
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")

print("Connecting to PostgreSQL...")
try:
    # connect_timeout=5 stops hanging after 5 seconds
    with psycopg.connect(db_url, connect_timeout=5, autocommit=True) as conn:
        with open("schema.sql", "r") as file:
            schema_sql = file.read()
        conn.execute(schema_sql)
        print("Success: schema.sql executed and extensions enabled!")
except Exception as e:
        print(f"Database error: {e}")