# RAG PoC

This repository is a small Retrieval-Augmented Generation (RAG) proof-of-concept.

It includes:

- FastAPI backend
- Streamlit frontend
- OpenAI for embeddings and completion (via environment variable)
- Postgres + pgvector for vector storage
- Docker Compose for local development and easy EC2 deployment

This README focuses on how to build, initialize the database, and run tests locally and in containers.



## Prerequisites

 - Linux (or WSL, e.g. `\\wsl$\Ubuntu\home\$USER\...`)
 - Docker
 - git
 - An OpenAI API key (set via `OPENAI_API_KEY` in your `.env`)



## One-time setup

1) Copy the example environment and fill it in:

`cp .env.example .env`

Edit `.env` and set OPENAI_API_KEY and any DB credentials you want



## Build and run locally

1) Set env vars:

`source ./set-env.sh`

2) Build and start the stack:

`docker compose up -d --build`

3) First time only: Initialize the database (create pgvector extension and  documents table)

Run these commands after the `db` container is running.

```bash
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c 'CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, content TEXT NOT NULL, embedding VECTOR(1536), metadata JSONB);'
```

4) Smoke test the backend and frontend

Backend: check health: `curl http://localhost:8000/health`

Frontend: open in browser: `http://localhost:8501`



## Running tests

Option A — run tests inside a container (matches CI)

This mounts the repository into a temporary backend container and runs pytest with the correct PYTHONPATH so the `backend` package is importable.

```bash
# from repo root (Bash)
docker compose run --rm -v "$PWD:/workspace" -w /workspace backend bash -lc "PYTHONPATH=/workspace pytest -q tests/backend -vv"
```

Option B — run tests locally in a venv

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
pytest -q tests/backend -vv
```


## Knowns bugs and limitations
- BUG: after recently refactoring code, `PostgresSyntaxError: syntax error at or near ":"`
- LIMITATION: currently, user must manually load the lore data; demo should pre-load this data
