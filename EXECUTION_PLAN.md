# Execution Plan — RAG PoC

Purpose
-------
This document is the single source of truth for implementing, building, testing, and running the RAG proof-of-concept in this repository. It contains the high-level goals, an explicit checklist mapped to current status, an ordered execution plan with commands, verification steps, and known risks.


Requirements checklist (visible)
- [x] FastAPI backend — basic app and `/health`; core routes implemented
- [x] Streamlit UI — `frontend/streamlit_app.py` present
- [x] OpenAI for embeddings & completion — async client implemented (httpx wrapper)
- [x] Postgres + pgvector vector storage — Compose uses pgvector image; extension/table initialized
- [x] Runs locally and on EC2 — Docker Compose + `infra/README-ec2.md` present
- [x] Docker Compose for local dev — `docker-compose.yml` present and tested
- [ ] Simple, production-ish architecture — separation present; hardening (secrets, reverse proxy, TLS) outstanding
- [x] Repo separation backend/frontend/infra — Done
- [x] Environment variables config — `.env.example` and runtime env loading present
- [ ] pytest tests for backend — basic smoke tests present; expand to cover services and edge cases
- [ ] Small, testable modules + DI — DI functions and small modules exist; expand unit tests and mocks

Notes about current state
- Containers build and run via `docker compose up -d --build`.
- The DB was initialized with the `vector` extension and `documents` table during development.
- A smoke pytest (tests/backend/test_query.py) passes when running tests in a container with the repo mounted.


Execution checklist (track progress)

- [x] Restore full backend implementation (core modules)
   - What: Add/replace `backend/app/services/openai_client.py` (async-safe), `backend/app/services/vector_store.py` (async SQLAlchemy usage), `backend/app/api/routes.py` (ingest/query logic).
   - Why: These are the core pieces of the RAG pipeline.
   - Verify: Unit tests for service functions and integration smoke via running the app and executing `/ingest` then `/query`.

- [x] Convert OpenAI client to async and add timeouts
   - What: Implemented an async httpx-based wrapper with a request timeout; retries/backoff are still recommended.
   - Why: Prevents blocking the event loop and improves reliability.
   - Verify: Integration test that mocks network calls; liveness under concurrent requests (left as next step).

- [ ] Implement VectorStore with SQLAlchemy models and migrations (partial)
   - What: `VectorStore` implemented using `create_async_engine` and raw SQL queries; Alembic migrations not yet added.
   - Why: Robust schema management is recommended.
   - Next: add Alembic and SQLAlchemy models if you want full migrations.

- [ ] Expand tests and dependency overrides (partial)
   - What: Basic smoke test exists; need to add unit tests that override FastAPI deps (`get_openai_client`, `get_vector_store`) with mocks and cover edge cases.
   - Why: Fast, deterministic test coverage is important before adding more features.

- [ ] CI: add GitHub Actions workflow
   - What: Add `.github/workflows/ci.yml` to run `pytest` and lint on PRs.

- [ ] Improve Docker images and Compose
   - What: Pin base images, run as non-root, add healthchecks, and consider multi-stage builds.

- [ ] Streamlit UX polish and backend auth
   - What: Add simple API key or token check and improve sources UI.

- [ ] EC2 docs & optional systemd service (partial)
   - What: `infra/README-ec2.md` contains minimal notes; expand with systemd example and env management.

- [ ] Performance and limits
   - What: Add request timeouts, concurrency limits and guard rails; consider caching embeddings.

- [ ] Final polish and follow-ups
   - What: Add more tests, CI checks, and optional metrics.

Tiny contract for handlers
- Inputs: JSON requests to `/ingest` (list of {id, text, metadata}) and `/query` ({query: str, top_k: int}).
- Outputs: JSON with `answer` and `sources` (list of metadata/content references).
- Error modes: missing env vars (400), DB unavailable (503), OpenAI failures (502).

Commands (quick copyable)
- Build & run stack:
  - PowerShell: `docker compose up -d --build`
  - Tear down: `docker compose down -v`
- Init DB (PowerShell):
  - `docker compose exec db psql -U $Env:POSTGRES_USER -d $Env:POSTGRES_DB -c "CREATE EXTENSION IF NOT EXISTS vector;"`
  - `docker compose exec db psql -U $Env:POSTGRES_USER -d $Env:POSTGRES_DB -c "CREATE TABLE IF NOT EXISTS documents (id TEXT PRIMARY KEY, content TEXT NOT NULL, embedding VECTOR(1536), metadata JSONB);"`
- Run tests (container):
  - `docker compose run --rm -v "${PWD}:/workspace" -w /workspace backend bash -lc "PYTHONPATH=/workspace pytest -q tests/backend -vv"`

Verification checklist (quality gates)
- Build: `docker compose up -d --build` — PASS (containers start)
- DB init: `CREATE EXTENSION vector` and `CREATE TABLE` — PASS (we executed in container)
- Unit tests: expand to cover services — currently minimal smoke tests PASS
- Lint/format: add `ruff` or `black` later

Risks & mitigations
- Risk: OpenAI calls cause high latency or cost. Mitigation: add caching, token limits, and model/timeouts.
- Risk: pgvector version mismatches. Mitigation: pin DB image to a known working `pgvector` image (we use `ankane/pgvector`).

How to use this file
- Update progress by editing this file and adding completed dates or PR links under each step.
- Treat the `Execution Plan` as the living roadmap for the repository.

Contact & ownership
- Primary implementer: repository maintainer (you). Ask me to take any of the numbered steps and I will implement them and update this file.
