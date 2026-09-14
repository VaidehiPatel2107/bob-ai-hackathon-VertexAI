# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Architecture Constraints (Non-Obvious)

- **The backend is implemented in FastAPI** — `src/backend/main.py` serves API routes for risk summaries, equipment details, outage zones, impact, recommendations, and `/api/copilot`.
- **`risk_engine.py` is active business logic** — it loads/scales equipment data, computes equipment+outage risk scores, and provides recommendation and impact helpers used by API routes.
- **A static frontend exists under `src/backend/static/`** — `index.html`, `app.js`, and `style.css` are served by FastAPI and rely on same-origin API calls.
- **The current Copilot feature is rule-based** — runtime responses come from backend logic, with IBM AI integration positioned as a future enhancement.
- **FastAPI routes are currently synchronous (`def`)** — plan async conversions only when introducing async I/O dependencies.
- **No database integration is wired yet** — architecture changes that add persistence still require choosing/installing the DB stack.
