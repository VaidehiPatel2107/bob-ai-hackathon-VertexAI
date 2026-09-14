# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Architecture Constraints (Non-Obvious)

- **The backend is a stub** — only two routes exist (`/` and `/health`). `risk_engine.py` is completely empty. Any architecture plan must treat this as a greenfield Python service.
- **No database driver is installed** — `psycopg2`, `sqlalchemy`, and `asyncpg` are absent from the venv despite `DATABASE_URL` being in `.env.example`. Plan to install one before adding DB access.
- **No frontend exists** — `src/` contains only `backend/`. Any UI layer must be built from scratch or added under `src/frontend/`.
- **watsonx.ai integration is not yet wired** — `WATSONX_API_KEY` / `WATSONX_PROJECT_ID` env vars are defined but no SDK (`ibm-watsonx-ai`) is installed. Budget an install + auth step when planning AI features.
- **FastAPI app is synchronous** — current route functions use `def`, not `async def`. If adding async I/O (DB, HTTP calls), convert to `async def` and ensure the right async driver is installed.
- **`annotated-doc 0.0.5`** is installed (a minor IBM internal utility for annotated type documentation) — likely a transitive dep; do not depend on it directly.
