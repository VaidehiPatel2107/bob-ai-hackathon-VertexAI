# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Project: GridGuard AI

Python/FastAPI backend for power grid equipment failure and outage risk prediction.
**Hackathon submission** — stack is Python 3.13, FastAPI 0.141.1, Pydantic v2, pandas, numpy.

## Commands

All commands run from `src/backend/` using the local venv:

```bash
# Activate venv (Windows)
src\backend\venv\Scripts\activate

# Run backend (from src/backend/)
uvicorn main:app --reload

# Or from project root
uvicorn src.backend.main:app --reload --app-dir .

# Install dependencies (from src/backend/)
pip install -r requirements.txt
```

**No test framework is installed** — pytest is not in the venv. There are no tests yet.
**No linter config** — no pyproject.toml, setup.cfg, or .flake8 anywhere.

## Critical Non-Obvious Facts

- **`requirements.txt` is UTF-16 encoded** (BOM artifact — characters are space-separated). Do not regenerate by copy-pasting its display; use `pip freeze` inside the venv instead.
- **`.env.example` is at `src/.env.example`**, not the project root. Copy with: `cp src/.env.example src/.env`
- **`risk_engine.py` is empty** — it is a placeholder. All risk/ML logic must be built there.
- **`src/backend/data/` is empty** — no data files exist yet.
- The FastAPI `app` object is at [`src/backend/main.py`](src/backend/main.py:3), importable as `src.backend.main:app`.
- Pydantic v2 is used (`pydantic==2.13.5`) — use `model_validator`, `field_validator`, not v1-style `@validator`.

## CI Validation (`.github/workflows/validate.yml`)

CI runs on every push and checks:
1. These files **must exist**: `README.md`, `submission.yaml`, `docs/problem-statement.md`, `docs/solution-overview.md`, `docs/architecture.md`, `docs/setup-guide.md`, `demo/demo-video-link.txt`
2. `submission.yaml` required fields: `team.name`, `team.track`, `team.lead.name`, `team.lead.email`, `submission.title`, `submission.problem_statement`, `submission.solution_summary`, at least 1 `key_features` entry
3. `team.track` must be exactly one of: `AI`, `DevOps`, `Sustainability`, `Open`
4. `submission.yaml` `tech_stack` arrays are **currently empty** — CI does not fail on this, but fill them before final submission
5. `demo/demo-video-link.txt` first line must not contain `your-demo-video-link-here`
6. `README.md` must not contain `[Your Project Title Here]` or `[Your Team Name]`

## Code Style

No enforced formatter. Follow the pattern in `main.py`: snake_case, type-annotated route functions, return plain `dict` from endpoints (FastAPI serializes automatically).
