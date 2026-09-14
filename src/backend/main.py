"""
GridGuard AI — FastAPI Application
===================================
Serves the GridGuard AI risk prediction API and the static frontend.

Data is loaded and scored once at startup from risk_engine.py.
No database, no external API calls — all scoring is in-memory pandas.

Copilot note
------------
POST /api/copilot is a rule-based stub.
Runtime label: "GridGuard Operations Copilot — rule-based MVP, designed for future IBM AI integration"
IBM Bob is the development assistant for this project; it does NOT power the runtime copilot.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

try:
    from . import risk_engine as re
except ImportError:
    import risk_engine as re

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = FastAPI(
    title="GridGuard AI",
    description="Power outage prediction and grid equipment failure advisor",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static frontend — directory is created in Sub-Task 4; mount silently if absent
_STATIC_DIR = Path(__file__).parent / "static"
if _STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

# ---------------------------------------------------------------------------
# Dataset — loaded and scored once at startup
# ---------------------------------------------------------------------------

_df: pd.DataFrame = pd.DataFrame()


@app.on_event("startup")
def startup() -> None:
    global _df
    raw = re.load_equipment()
    scored = re.score_equipment(raw)
    scored = re.score_outage_risk(scored)
    _df = scored


def _get_asset(asset_id: str) -> pd.Series:
    """Return the row for *asset_id* or raise HTTP 404."""
    row = _df[_df["asset_id"] == asset_id]
    if row.empty:
        raise HTTPException(status_code=404, detail=f"Asset '{asset_id}' not found")
    return row.iloc[0]


# ---------------------------------------------------------------------------
# Root — serves index.html when static dir exists, otherwise API info
# ---------------------------------------------------------------------------

@app.get("/", include_in_schema=False)
def root():
    index = _STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {
        "message": "GridGuard AI API is running",
        "docs": "/docs",
        "status": "success",
    }


@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy", "assets_loaded": len(_df)}


# ---------------------------------------------------------------------------
# Equipment endpoints
# ---------------------------------------------------------------------------

@app.get("/api/equipment", tags=["Equipment"])
def list_equipment():
    """All 50 assets with both risk scores."""
    cols = [
        "asset_id", "name", "type", "zone",
        "equipment_risk_score", "equipment_risk_label",
        "outage_risk_score", "outage_risk_label",
    ]
    return _df[cols].to_dict(orient="records")


@app.get("/api/equipment/{asset_id}", tags=["Equipment"])
def get_equipment(asset_id: str):
    """Single asset: all fields + both risk scores + recommendations + impact."""
    row = _get_asset(asset_id)
    data = row.to_dict()
    # Convert numpy types to plain Python for JSON serialisation
    data = {k: (v.item() if hasattr(v, "item") else v) for k, v in data.items()}
    data["recommendations"] = re.get_recommendations(row)
    data["impact"] = re.get_impact(row)
    return data


# ---------------------------------------------------------------------------
# Risk summary endpoints
# ---------------------------------------------------------------------------

@app.get("/api/risk/summary", tags=["Risk"])
def risk_summary():
    """Portfolio-level risk counts and highest-risk zone."""
    eq = _df["equipment_risk_label"]
    out = _df["outage_risk_label"]

    zone_avg = _df.groupby("zone")["equipment_risk_score"].mean()
    highest_risk_zone = zone_avg.idxmax()

    return {
        "total_assets":            len(_df),
        "critical_equipment":      int((eq == "CRITICAL").sum()),
        "high_equipment":          int((eq == "HIGH").sum()),
        "medium_equipment":        int((eq == "MEDIUM").sum()),
        "low_equipment":           int((eq == "LOW").sum()),
        "critical_outage":         int((out == "CRITICAL").sum()),
        "high_outage":             int((out == "HIGH").sum()),
        "highest_risk_zone":       highest_risk_zone,
        "avg_equipment_risk_score": round(float(_df["equipment_risk_score"].mean()), 2),
    }


@app.get("/api/risk/top", tags=["Risk"])
def top_risk(n: int = 10):
    """Top-N assets by equipment risk score (descending)."""
    n = max(1, min(n, len(_df)))
    cols = [
        "asset_id", "name", "type", "zone",
        "equipment_risk_score", "equipment_risk_label",
        "outage_risk_score", "outage_risk_label",
    ]
    top = _df.nlargest(n, "equipment_risk_score")[cols]
    return top.to_dict(orient="records")


# ---------------------------------------------------------------------------
# Outage risk by zone
# ---------------------------------------------------------------------------

@app.get("/api/outage-risk", tags=["Outage Risk"])
def outage_risk_by_zone():
    """Outage risk aggregated per zone."""
    high_crit = {"HIGH", "CRITICAL"}
    result = []
    for zone, group in _df.groupby("zone"):
        result.append({
            "zone":                     zone,
            "avg_outage_risk_score":    round(float(group["outage_risk_score"].mean()), 2),
            "max_outage_risk_score":    round(float(group["outage_risk_score"].max()), 2),
            "assets_at_high_or_critical": int(group["outage_risk_label"].isin(high_crit).sum()),
        })
    result.sort(key=lambda x: x["avg_outage_risk_score"], reverse=True)
    return result


# ---------------------------------------------------------------------------
# Impact analysis
# ---------------------------------------------------------------------------

@app.get("/api/impact/{asset_id}", tags=["Impact"])
def get_impact(asset_id: str):
    """Impact analysis for one asset. All figures are synthetic demo estimates."""
    row = _get_asset(asset_id)
    return re.get_impact(row)


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

@app.get("/api/recommendations/{asset_id}", tags=["Recommendations"])
def get_recommendations(asset_id: str):
    """Preventive action recommendations for one asset."""
    row = _get_asset(asset_id)
    return {
        "asset_id":               asset_id,
        "equipment_risk_label":   str(row["equipment_risk_label"]),
        "outage_risk_label":      str(row["outage_risk_label"]),
        "recommendations":        re.get_recommendations(row),
    }


# ---------------------------------------------------------------------------
# GridGuard Operations Copilot (rule-based stub)
# ---------------------------------------------------------------------------

class CopilotRequest(BaseModel):
    question: str


@app.post("/api/copilot", tags=["Copilot"])
def copilot(request: CopilotRequest):
    """
    GridGuard Operations Copilot — rule-based MVP, designed for future IBM AI integration.
    Accepts a free-text question and returns a natural-language answer based on live risk data.
    """
    answer = re.copilot_answer(request.question, _df)
    return {
        "answer": answer,
        "model":  re.COPILOT_LABEL,
    }
