# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Documentation Context (Non-Obvious)

- **`docs/` files are mostly template placeholders** — `architecture.md`, `setup-guide.md`, `solution-overview.md`, and `problem-statement.md` still contain `[e.g., ...]` placeholder text. The actual system design is not yet documented there.
- **`src/README.md` describes generic project patterns** (web app, data/AI, CLI) — it is a hackathon scaffold template, not a description of GridGuard AI's actual structure.
- **The authoritative problem/solution description** is in `submission.yaml` (`problem_statement` and `solution_summary` fields), not in the docs folder.
- **`demo/demo-video-link.txt` must contain a real URL** on its first line — CI reads only line 1.
- **`submission.yaml` `tech_stack` arrays** (`languages`, `frameworks`, `ibm_technologies`, etc.) are empty `[]` and need to be populated. CI does not block on them but they appear in judge evaluation.
