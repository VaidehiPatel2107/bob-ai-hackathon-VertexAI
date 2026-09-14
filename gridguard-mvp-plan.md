# GridGuard AI — MVP Implementation Plan (Revised)

## Overview

Build a working GridGuard AI demo using the existing FastAPI skeleton, pure
pandas-based risk scoring, and a minimal vanilla HTML/CSS/JS frontend.
No database, no external ML service, no build toolchain.
Everything runs offline with `uvicorn main:app --reload` from `src/backend/`.

The "GridGuard Operations Copilot" is a rule-based stub at runtime —
explicitly labelled as "rule-based MVP, designed for future IBM AI integration."
IBM Bob is our development assistant; no runtime Bob/watsonx API is configured.

---

## Architecture

```
Browser
  └─ index.html (served by FastAPI StaticFiles from src/backend/static/)
       └─ fetch() calls to API endpoints

FastAPI (src/backend/main.py)
  ├─ GET  /                              → serves index.html
  ├─ GET  /health                        → health check
  ├─ GET  /api/equipment                 → all assets with risk scores
  ├─ GET  /api/equipment/{id}            → single asset detail
  ├─ GET  /api/risk/summary              → portfolio-level risk summary
  ├─ GET  /api/risk/top?n=10             → top-N highest equipment risk
  ├─ GET  /api/outage-risk               → outage risk per zone (separate model)
  ├─ GET  /api/impact/{id}              → impact analysis (separate from risk)
  ├─ GET  /api/recommendations/{id}     → preventive action list
  └─ POST /api/copilot                   → rule-based NL copilot (stub)

risk_engine.py
  ├─ load_equipment()                   → loads CSV, returns DataFrame
  ├─ score_equipment(df)                → equipment failure risk (0–100 + label)
  ├─ score_outage_risk(df)              → outage risk (separate model, 0–100 + label)
  ├─ get_impact(row)                    → impact analysis dict (customers, energy, cost)
  ├─ get_recommendations(row)           → rule-based list[str]
  └─ copilot_answer(question, df)       → rule-based text response (stub)

src/backend/data/equipment.csv
  → 50 synthetic assets across North Grid / South Grid / Industrial Zone
```

---

## Data Model

`src/backend/data/equipment.csv` columns:

| Column | Type | Notes |
|---|---|---|
| `asset_id` | str | e.g. "TF-001" |
| `name` | str | Human-readable name |
| `type` | str | Transformer / Power Line / Substation / Circuit Breaker |
| `zone` | str | North Grid / South Grid / Industrial Zone |
| `age_years` | int | 2–45 |
| `load_pct` | float | 35–110 (>100 = overloaded) |
| `temp_c` | float | 35–95 |
| `last_maintenance_days` | int | 10–730 |
| `failure_history_count` | int | 0–8 |
| `outage_history_count` | int | 0–6 (separate from equipment failures) |
| `weather_severity` | int | 0–3 (0=clear, 1=mild, 2=moderate, 3=severe) |
| `asset_criticality` | int | 1–3 (1=standard, 2=important, 3=critical infrastructure) |
| `customers_affected` | int | 200–15 000 |
| `critical_facilities` | int | 0–5 (hospitals, schools, emergency services on this asset) |
| `peak_load_mw` | float | 0.5–50.0 MW |

---

## Risk Models

### Model 1 — Equipment Failure Risk

Predicts the likelihood that the physical asset will fail.

```
equipment_risk_score = (
    age_factor       * 0.20   # age_years / 45 * 100
  + load_factor      * 0.25   # load_pct / 110 * 100
  + temp_factor      * 0.20   # (temp_c - 35) / 60 * 100
  + maint_factor     * 0.15   # last_maintenance_days / 730 * 100
  + history_factor   * 0.10   # failure_history_count / 8 * 100
  + weather_factor   * 0.10   # weather_severity / 3 * 100
)  → clamped to 0–100

risk_label:
  0–30   → LOW
  31–60  → MEDIUM
  61–80  → HIGH
  81–100 → CRITICAL
```

### Model 2 — Outage Risk (separate model)

Predicts the likelihood and severity of a power outage event.
Combines equipment condition, operational stress, environmental factors,
historical outage tendency, and asset criticality.

```
outage_risk_score = (
    equipment_risk_score * 0.30   # underlying equipment condition
  + load_factor          * 0.20   # load_pct / 110 * 100
  + weather_factor       * 0.20   # weather_severity / 3 * 100
  + outage_history_factor* 0.15   # outage_history_count / 6 * 100
  + criticality_factor   * 0.15   # (asset_criticality - 1) / 2 * 100
)  → clamped to 0–100

outage_label: same thresholds as equipment risk
```

The two scores are independent. A newly maintained but heavily loaded critical
substation can have LOW equipment risk and HIGH outage risk.

---

## Impact Analysis (separate from risk prediction)

`get_impact(row)` returns a dict — computed from asset data, not from risk scores.
All monetary values are **explicitly synthetic demo assumptions** — clearly
documented in API responses and in the frontend.

```python
{
    "asset_id":                  str,
    "customers_affected":        int,       # from CSV
    "critical_facilities":       int,       # from CSV
    "estimated_downtime_hours":  float,     # base 2h + 0.5h per failure_history_count
    "estimated_energy_loss_mwh": float,     # peak_load_mw * estimated_downtime_hours
    "estimated_economic_impact_usd": float, # customers_affected * downtime * 4.50
                                            # SYNTHETIC ASSUMPTION: $4.50/customer/hour
    "_note": "All impact figures are synthetic demo estimates for illustration only."
}
```

---

## Recommendations (rule-based)

`get_recommendations(row)` returns list[str]. Multiple rules can fire.

| Condition | Recommendation |
|---|---|
| risk_label == CRITICAL | "Immediate shutdown and emergency inspection required" |
| load_pct > 95 | "Reduce load — asset is operating above rated capacity" |
| temp_c > 80 | "Thermal inspection required — overheating detected" |
| last_maintenance_days > 365 | "Schedule preventive maintenance — overdue by >1 year" |
| failure_history_count >= 5 | "Review asset lifecycle — repeated failure history" |
| weather_severity >= 2 | "Deploy weather hardening measures" |
| age_years > 30 | "Asset approaching end of operational life — plan replacement" |
| asset_criticality == 3 and outage_label in {HIGH,CRITICAL} | "Priority response required — critical infrastructure asset" |

---

## Copilot

Endpoint: `POST /api/copilot`  
Runtime label: **"GridGuard Operations Copilot — rule-based MVP, designed for future IBM AI integration"**  
This is NOT described as IBM Bob-powered at runtime.

Pattern matching (case-insensitive) against live DataFrame:

| Question contains | Response |
|---|---|
| "critical" / "worst" | Top-3 CRITICAL assets by name + score |
| "high risk" | Count of HIGH+CRITICAL assets, zone with most |
| "recommend" / "what should" | Recommendations for top-risk asset (or named asset) |
| "outage" | Zone with highest average outage risk |
| "impact" | Asset with highest economic impact estimate |
| fallback | Summary: X assets analysed, Y at HIGH/CRITICAL risk |

---

## Sub-Task 1 — Synthetic Equipment Data

**Owner:** Aadya  
**Intent:** Create the seed dataset. All downstream logic depends on it.

**Expected Outcomes:**
- `src/backend/data/equipment.csv` with exactly 50 rows
- All columns listed in the Data Model section present
- Distribution: 20 Transformers, 15 Power Lines, 10 Substations, 5 Circuit Breakers
- Zones: North Grid (~17), South Grid (~17), Industrial Zone (~16)
- At least 5 rows that will score CRITICAL on equipment risk
- At least 3 rows where outage risk will be HIGH/CRITICAL despite lower equipment risk
  (to demonstrate the two models are independent)

**Todo:**
- [x] Create `src/backend/data/equipment.csv` with all 50 rows
- [x] Verify column names exactly match the Data Model table above
- [x] Verify at least 5 assets have high-risk-driving values
  (e.g. age_years > 35, load_pct > 95, last_maintenance_days > 600)

**Status:** [x] done

---

## Sub-Task 2 — Risk Engine

**Owner:** Vaidehi  
**Intent:** Implement all scoring, impact, recommendation, and copilot logic in `risk_engine.py`.

**Expected Outcomes:**
- Module exports: `load_equipment`, `score_equipment`, `score_outage_risk`,
  `get_impact`, `get_recommendations`, `copilot_answer`
- `score_equipment(df)` adds `equipment_risk_score` and `equipment_risk_label`
- `score_outage_risk(df)` adds `outage_risk_score` and `outage_risk_label`
  (called after `score_equipment` since it uses `equipment_risk_score`)
- `get_impact(row)` returns dict with `_note` field documenting synthetic assumptions
- `get_recommendations(row)` returns list[str] — always at least one item for HIGH/CRITICAL
- `copilot_answer(question, df)` returns str — never crashes regardless of input

**Todo:**
- [x] Implement `load_equipment()` — reads CSV, returns DataFrame
- [x] Implement `score_equipment(df)` — adds `equipment_risk_score`, `equipment_risk_label`
- [x] Implement `score_outage_risk(df)` — adds `outage_risk_score`, `outage_risk_label`
- [x] Implement `get_impact(row)` — returns dict with all five impact fields + `_note`
- [x] Implement `get_recommendations(row)` — all 8 rule conditions
- [x] Implement `copilot_answer(question, df)` — all 5 patterns + fallback
- [x] Smoke test: all functions verified against live dataset

**Relevant Files:**
- `src/backend/risk_engine.py`
- `src/backend/data/equipment.csv` (Sub-Task 1)

**Dependencies:** Sub-Task 1 must be complete.

**Status:** [x] done

---

## Sub-Task 3 — API Endpoints

**Owner:** Vaidehi  
**Intent:** Wire all risk engine functions to FastAPI routes.

**Expected Outcomes:**
- All 9 endpoints return valid JSON with correct structure
- FastAPI Swagger docs at `/docs` list all endpoints
- `StaticFiles` mounted so `index.html` is served at `http://localhost:8000/`
- CORS enabled (allow all origins for demo)
- Unknown `asset_id` returns HTTP 404, not 500
- Equipment risk and outage risk fields are clearly named separately in responses

**Endpoint Specifications:**

```
GET /api/equipment
  → list[{asset_id, name, type, zone, equipment_risk_score, equipment_risk_label,
           outage_risk_score, outage_risk_label}]

GET /api/equipment/{asset_id}
  → {all CSV fields, equipment_risk_score, equipment_risk_label,
     outage_risk_score, outage_risk_label,
     recommendations: list[str], impact: dict}

GET /api/risk/summary
  → {total_assets, critical_equipment, high_equipment, medium_equipment, low_equipment,
     critical_outage, high_outage, highest_risk_zone, avg_equipment_risk_score}

GET /api/risk/top?n=10
  → top-N assets by equipment_risk_score desc

GET /api/outage-risk
  → per zone: {zone, avg_outage_risk_score, max_outage_risk_score,
               assets_at_high_or_critical: int}

GET /api/impact/{asset_id}
  → {asset_id, customers_affected, critical_facilities, estimated_downtime_hours,
     estimated_energy_loss_mwh, estimated_economic_impact_usd, _note}

GET /api/recommendations/{asset_id}
  → {asset_id, equipment_risk_label, outage_risk_label, recommendations: list[str]}

POST /api/copilot
  body: {"question": "..."}
  → {"answer": "...", "model": "rule-based MVP, designed for future IBM AI integration"}
```

**Todo:**
- [x] Add `from fastapi.middleware.cors import CORSMiddleware`, allow all origins
- [x] Load data once at startup: `@app.on_event("startup")`
- [x] Mount `StaticFiles` silently if `static/` dir exists (created in Sub-Task 4)
- [x] Implement all 8 GET + 1 POST endpoint functions
- [x] Return HTTP 404 for unknown asset_id on `/api/equipment/{id}`, `/api/impact/{id}`, `/api/recommendations/{id}`

**Dependencies:** Sub-Task 2 must be complete.

**Status:** [x] done

---

## Sub-Task 4 — Frontend Dashboard

**Owners:** Devanshi (UI/design, layout, styling) + Vaidehi (API integration, dynamic data rendering, risk visualisations, copilot wiring)  
**Intent:** Deliver a working single-page dashboard served by FastAPI with no build step.

**Expected Outcomes:**
- `src/backend/static/index.html` loads at `http://localhost:8000/` with no console errors
- Summary cards display: Total Assets / CRITICAL / HIGH / MEDIUM counts
- Assets table: Asset Name | Zone | Type | Equip. Risk | Outage Risk — colour-coded badges
- Clicking a row opens a detail panel: all risk scores, recommendations list, impact figures
- Impact panel includes a visible disclaimer: "⚠️ All impact figures are synthetic demo estimates"
- Copilot panel: text input + submit button → displays answer + "GridGuard Operations Copilot — rule-based MVP, designed for future IBM AI integration" label
- No external JS/CSS frameworks loaded from CDN (offline demo safety)

**Todo:**
- [x] Create `src/backend/static/` directory
- [x] Create `src/backend/static/index.html` — full HTML structure
- [x] Create `src/backend/static/style.css` — dark utility theme, no CDN
- [x] Create `src/backend/static/app.js` — all API wiring, divergence detection
- [x] Implement summary cards section (fetch `/api/risk/summary`)
- [x] Implement distribution bars (fetch `/api/equipment`)
- [x] Implement top-10 assets table (fetch `/api/risk/top?n=10`)
- [x] Implement zone outage bars (fetch `/api/outage-risk`)
- [x] Implement row click → detail panel (fetch `/api/equipment/{id}`)
- [x] Implement impact section with synthetic data disclaimer from API `_note`
- [x] Implement copilot panel (POST `/api/copilot`) — label set from API `model` field
- [x] Divergence callout rendered when asset is LOW/MEDIUM equip + HIGH/CRITICAL outage

**Dependencies:** Sub-Task 3 must be complete (endpoints must be live).

**Status:** [x] done

---

## Sub-Task 5 — Smoke Tests

**Intent:** Verify all API endpoints and the frontend load correctly without
introducing a full test framework.

**Expected Outcomes:**
- A single Python script `src/backend/smoke_test.py` that:
  - Starts nothing — assumes `uvicorn main:app` is already running on port 8000
  - Makes one HTTP request to each of the 9 endpoints
  - Asserts HTTP 200 and presence of expected top-level keys in the JSON response
  - Asserts HTTP 404 for a known-invalid asset_id
  - Prints PASS / FAIL per endpoint
  - Exits with code 0 if all pass, 1 if any fail
- Manual frontend check: open `http://localhost:8000/` and confirm all 4 sections render

**Todo:**
- [ ] Create `src/backend/smoke_test.py` using only `urllib.request` (stdlib — no pytest needed)
- [ ] Test all 9 endpoints including the 404 case
- [ ] Run the script against a live server and confirm all PASS

**Dependencies:** Sub-Tasks 3 and 4 must be complete.

**Status:** [ ] pending

---

## Sub-Task 6 — Submission Completion

**Owner:** Durva + All  
**Intent:** Ensure the repo passes CI validation and is ready for judge review.

**Expected Outcomes:**
- `.github/workflows/validate.yml` passes on push (no failures)
- All `submission.yaml` fields filled
- All `docs/` files contain real project content (no template placeholders)
- `demo/demo-video-link.txt` line 1 is a real URL
- `README.md` has no `[bracket]` placeholders

### submission.yaml updates needed

```yaml
languages: ["Python"]
frameworks: ["FastAPI", "pandas", "numpy"]
ibm_technologies: ["IBM Bob"]
databases: []
other: ["Uvicorn", "Pydantic v2"]
what_we_are_most_proud_of: >
  [Fill in — e.g. the dual risk model architecture, or the offline demo reliability]
known_limitations: >
  [Fill in — e.g. synthetic data, rule-based copilot, no authentication]
```

**Todo:**
- [ ] Update `submission.yaml` — fill all empty/placeholder fields
- [ ] Update `README.md` — replace all `[bracket]` placeholders
- [ ] Write real content in `docs/problem-statement.md`
- [ ] Write real content in `docs/solution-overview.md`
- [ ] Write real content in `docs/architecture.md` (use actual system diagram)
- [ ] Write real content in `docs/setup-guide.md` (actual run commands)
- [ ] Update `demo/demo-video-link.txt` with real video URL (after recording)
- [ ] Add screenshots to `demo/screenshots/`

**Status:** [ ] pending

---

## Actual Run Commands (for setup-guide.md)

```bash
# Windows — from project root
cd src\backend
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
# Open http://localhost:8000

# macOS/Linux — from project root
cd src/backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
# Open http://localhost:8000

# Smoke test (with server running in another terminal)
python smoke_test.py
```

---

## Key Constraints (all sub-tasks must respect these)

- No database. Data loaded from CSV at startup into a module-level DataFrame.
- No external API calls. All scoring is in-memory pandas.
- No CDN dependencies in frontend — demo must work fully offline.
- Pydantic v2 syntax only (`model_config`, `@field_validator`, not `@validator`).
- `risk_engine.py` must not import from `main.py` (one-way dependency).
- `requirements.txt` is UTF-16 encoded — regenerate with `pip freeze` inside venv, never edit manually.
- Copilot is NEVER described as "IBM Bob-powered" at runtime.
  Runtime label: "GridGuard Operations Copilot — rule-based MVP, designed for future IBM AI integration."
- All monetary impact values must carry the note: "Synthetic demo estimate: $4.50/customer/hour assumption."
- Two risk models (equipment failure risk and outage risk) are always kept separate in API responses, UI, and documentation.
