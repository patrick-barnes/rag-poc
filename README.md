# RAG PoC

This repository is a small Retrieval-Augmented Generation (RAG) proof-of-concept.

It includes:

- FastAPI backend
- Streamlit frontend
- OpenAI for embeddings and completion (via environment variable)
- Postgres + pgvector for vector storage
- Docker Compose for local development and easy EC2 deployment

This README focuses on how to build, initialize the database, and run tests locally and in containers.

Prerequisites
 - Docker Desktop (or Docker Engine + Compose v2)
 - git, and a shell (Bash on Linux is used in examples)
 - An OpenAI API key (set via `OPENAI_API_KEY` in your `.env`)

Quick start (Docker, recommended)

1) Copy the example environment and fill it in:

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY and any DB credentials you want
```

2) Build and start the stack:

```bash
docker compose up -d --build
```

3) Initialize the database (create the pgvector extension and the documents table).
	Run these commands after the `db` container is running.

```bash
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker compose exec db psql -U $POSTGRES_USER -d $POSTGRES_DB -c 'CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, content TEXT NOT NULL, embedding VECTOR(1536), metadata JSONB);'
```

4) Smoke test the backend and frontend

```bash
# backend health
curl http://localhost:8000/health

# open Streamlit in a browser at http://localhost:8501
```

Running tests

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

Notes and troubleshooting
- If the `db` container cannot create the `vector` extension, ensure you are using the bundled image (the Compose file uses a pgvector-enabled image). If you change the image, you must install the `vector` extension in that Postgres build.
- If Docker CLI reports it cannot connect, start Docker Desktop or ensure the Docker daemon is running.
- The `.env.example` file lists the environment variables used by the services; copy it to `.env` and keep secrets out of source control.
- For production or EC2: see `infra/README-ec2.md` for minimal deployment notes; use a proper reverse proxy and TLS in production.

Development notes
- The backend code is located under `backend/app/`. The FastAPI app factory is `backend/app/main.py`.
- The frontend Streamlit app is `frontend/streamlit_app.py`.
- Tests live under `tests/backend/` and are written to use FastAPI dependency overrides where appropriate.

If you'd like, I can now restore the fuller backend implementations (OpenAI wrapper, vector store, ingest/query logic) and convert the OpenAI client to a proper async implementation — tell me which to prioritize next.
