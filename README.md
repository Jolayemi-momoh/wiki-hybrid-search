# Local Wikipedia Hybrid Search Engine

A local, high-performance hybrid search engine combining **Full-Text Search (BM25)** and **Vector Search (pgvector)** over 5,000 Wikipedia articles using **Reciprocal Rank Fusion (RRF)**. Served via FastAPI with a dark-mode web UI.

## ?? Architecture
- **Database**: PostgreSQL 16 running in Docker (	imescaledb-ha:pg16) with ector and ectorscale extensions.
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions).
- **Search Algorithm**: Reciprocal Rank Fusion (RRF) merging BM25 keyword matching (with GIN index) and Cosine Distance HNSW vector indexing.
- **Backend**: FastAPI with CORS middleware and single-port HTML serving.
- **Dataset**: Hugging Face wikimedia/wikipedia (Simple English).

## ?? Getting Started

### 1. Prerequisites
- Windows PowerShell
- Docker Desktop running WSL 2
- Python 3.10+

### 2. Database Setup
 = @"
# Local Wikipedia Hybrid Search Engine

A local, high-performance hybrid search engine combining **Full-Text Search (BM25)** and **Vector Search (pgvector)** over 5,000 Wikipedia articles using **Reciprocal Rank Fusion (RRF)**. Served via FastAPI with a dark-mode web UI.

## ?? Architecture
- **Database**: PostgreSQL 16 running in Docker (	imescaledb-ha:pg16) with ector and ectorscale extensions.
- **Embedding Model**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensions).
- **Search Algorithm**: Reciprocal Rank Fusion (RRF) merging BM25 keyword matching (with GIN index) and Cosine Distance HNSW vector indexing.
- **Backend**: FastAPI with CORS middleware and single-port HTML serving.
- **Dataset**: Hugging Face wikimedia/wikipedia (Simple English).

## ?? Getting Started

### 1. Prerequisites
- Windows PowerShell
- Docker Desktop running WSL 2
- Python 3.10+

### 2. Database Setup
docker run -d --name pg_search -p 5433:5432 -e POSTGRES_PASSWORD=mysecretpassword timescale/timescaledb-ha:pg16-latest
# Install dependencies
pip install -r requirements.txt

# Initialize schema, stream dataset, and generate embeddings
python init_db.py
python load_data.py
python update_schema.py
python generate_embeddings.py
python add_gin_index.py
### 4. Run the API & Web UI
uvicorn main:app --reload --port 8000
Access the search interface at [http://127.0.0.1:8000](http://127.0.0.1:8000) or interact with Swagger API docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).
