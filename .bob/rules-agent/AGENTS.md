# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Coding Rules (Non-Obvious)

- **`risk_engine.py` is the designated ML/risk logic module** — all scoring, prediction, and prioritization logic goes there, not in `main.py`.
- **Pydantic v2 API**: use `model_config = ConfigDict(...)`, `@model_validator(mode='after')`, `@field_validator`. The old `class Config` and `@validator` syntax will raise deprecation errors.
- **No test runner installed** — if adding tests, install `pytest` and `httpx` first (`pip install pytest httpx`), then run `pytest` from `src/backend/`.
- **venv is at `src/backend/venv/`** — always activate it before running pip or python commands.
- **Return plain `dict` from FastAPI endpoints** — Pydantic `BaseModel` response classes are optional but preferred for documented APIs; FastAPI will serialize either.
- **`src/backend/data/equipment.csv` is a required committed runtime dataset** — the backend loads it at startup and `.gitignore` keeps this file tracked.
- **`requirements.txt` encoding**: the file is UTF-16. If regenerating, run `pip freeze > requirements.txt` inside the activated venv; do not manually edit the existing file.
