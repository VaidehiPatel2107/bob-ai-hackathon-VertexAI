"""
GridGuard AI — Risk Engine
==========================
Provides two independent risk models, impact analysis, preventive
recommendations, and a rule-based operations copilot stub.

All scoring is in-memory pandas — no external API calls, no database.

Copilot note
------------
The copilot_answer() function is a rule-based MVP stub.
It is labelled at runtime as:
  "GridGuard Operations Copilot — rule-based MVP, designed for future IBM AI integration"
IBM Bob is the development assistant for this project; it does NOT power
the runtime copilot.

Impact note
-----------
All figures returned by get_impact() are synthetic demo estimates.
The $4.50/customer/hour economic assumption is documented explicitly
in every impact response via the '_note' field.
"""

from __future__ import annotations

import os
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "equipment.csv"

# Equipment failure risk weights (must sum to 1.0)
_EQ_WEIGHTS = {
    "age":         0.20,
    "load":        0.25,
    "temp":        0.20,
    "maintenance": 0.15,
    "failure_history": 0.10,
    "weather":     0.10,
}

# Outage risk weights (must sum to 1.0)
_OUT_WEIGHTS = {
    "equipment_risk": 0.30,
    "load":           0.20,
    "weather":        0.20,
    "outage_history": 0.15,
    "criticality":    0.15,
}

# Normalisation denominators (match CSV value ranges)
_NORM = {
    "age_years":              45.0,
    "load_pct":              110.0,
    "temp_c_range":           60.0,   # (temp_c - 35) / 60
    "temp_c_min":             35.0,
    "last_maintenance_days": 730.0,
    "failure_history_count":   8.0,
    "weather_severity":        3.0,
    "outage_history_count":    6.0,
    "asset_criticality_range": 2.0,   # (criticality - 1) / 2
}

# Impact assumption: economic cost per customer per hour of outage
_COST_PER_CUSTOMER_HOUR_USD = 4.50

_IMPACT_NOTE = (
    "All impact figures are synthetic demo estimates for illustration only. "
    "Economic cost assumes $4.50 per customer per hour of outage — "
    "a conservative utility industry proxy used for demonstration purposes."
)

COPILOT_LABEL = (
    "GridGuard Operations Copilot — rule-based MVP, "
    "designed for future IBM AI integration"
)


# ---------------------------------------------------------------------------
# Label helper
# ---------------------------------------------------------------------------

def _risk_label(score: float) -> str:
    """Map a 0–100 score to LOW / MEDIUM / HIGH / CRITICAL."""
    if score >= 81:
        return "CRITICAL"
    if score >= 61:
        return "HIGH"
    if score >= 31:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_equipment() -> pd.DataFrame:
    """Load the equipment CSV and return a clean DataFrame."""
    df = pd.read_csv(_DATA_PATH)
    return df.copy()


# ---------------------------------------------------------------------------
# Model 1 — Equipment Failure Risk
# ---------------------------------------------------------------------------

def score_equipment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'equipment_risk_score' (float, 0–100) and 'equipment_risk_label'
    columns to *df* (in-place copy returned).

    Formula (weighted sum, clamped to [0, 100]):
        age_factor       * 0.20   (age_years / 45 * 100)
      + load_factor      * 0.25   (load_pct / 110 * 100)
      + temp_factor      * 0.20   ((temp_c - 35) / 60 * 100)
      + maint_factor     * 0.15   (last_maintenance_days / 730 * 100)
      + history_factor   * 0.10   (failure_history_count / 8 * 100)
      + weather_factor   * 0.10   (weather_severity / 3 * 100)
    """
    df = df.copy()

    age_f      = df["age_years"]              / _NORM["age_years"]              * 100
    load_f     = df["load_pct"]               / _NORM["load_pct"]               * 100
    temp_f     = (df["temp_c"] - _NORM["temp_c_min"]) / _NORM["temp_c_range"]  * 100
    maint_f    = df["last_maintenance_days"]  / _NORM["last_maintenance_days"]  * 100
    history_f  = df["failure_history_count"]  / _NORM["failure_history_count"]  * 100
    weather_f  = df["weather_severity"]       / _NORM["weather_severity"]       * 100

    score = (
        age_f      * _EQ_WEIGHTS["age"]
        + load_f   * _EQ_WEIGHTS["load"]
        + temp_f   * _EQ_WEIGHTS["temp"]
        + maint_f  * _EQ_WEIGHTS["maintenance"]
        + history_f * _EQ_WEIGHTS["failure_history"]
        + weather_f * _EQ_WEIGHTS["weather"]
    ).clip(0, 100)

    df["equipment_risk_score"] = score.round(2)
    df["equipment_risk_label"] = score.apply(_risk_label)
    return df


# ---------------------------------------------------------------------------
# Model 2 — Outage Risk (separate model)
# ---------------------------------------------------------------------------

def score_outage_risk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add 'outage_risk_score' (float, 0–100) and 'outage_risk_label' columns.

    Must be called AFTER score_equipment() — uses 'equipment_risk_score'.

    Formula (weighted sum, clamped to [0, 100]):
        equipment_risk_score * 0.30   (underlying equipment condition)
      + load_factor          * 0.20   (load_pct / 110 * 100)
      + weather_factor       * 0.20   (weather_severity / 3 * 100)
      + outage_history_factor* 0.15   (outage_history_count / 6 * 100)
      + criticality_factor   * 0.15   ((asset_criticality - 1) / 2 * 100)

    The two models are independent: a recently maintained but critically
    positioned asset under severe weather can have LOW equipment risk and
    HIGH outage risk.
    """
    if "equipment_risk_score" not in df.columns:
        raise ValueError("Call score_equipment(df) before score_outage_risk(df).")

    df = df.copy()

    load_f      = df["load_pct"]             / _NORM["load_pct"]               * 100
    weather_f   = df["weather_severity"]     / _NORM["weather_severity"]       * 100
    out_hist_f  = df["outage_history_count"] / _NORM["outage_history_count"]   * 100
    crit_f      = (df["asset_criticality"] - 1) / _NORM["asset_criticality_range"] * 100

    score = (
        df["equipment_risk_score"] * _OUT_WEIGHTS["equipment_risk"]
        + load_f      * _OUT_WEIGHTS["load"]
        + weather_f   * _OUT_WEIGHTS["weather"]
        + out_hist_f  * _OUT_WEIGHTS["outage_history"]
        + crit_f      * _OUT_WEIGHTS["criticality"]
    ).clip(0, 100)

    df["outage_risk_score"] = score.round(2)
    df["outage_risk_label"] = score.apply(_risk_label)
    return df


# ---------------------------------------------------------------------------
# Impact Analysis
# ---------------------------------------------------------------------------

def get_impact(row: pd.Series) -> dict:
    """
    Return impact analysis for a single asset row.

    Computed from asset data (CSV fields), NOT from risk scores.
    All monetary figures are synthetic demo estimates — see '_note'.

    Fields returned:
        customers_affected         — from CSV
        critical_facilities        — from CSV
        estimated_downtime_hours   — base 2h + 0.5h per failure_history_count
        estimated_energy_loss_mwh  — peak_load_mw * estimated_downtime_hours
        estimated_economic_impact_usd — customers_affected * downtime * $4.50
        _note                      — explicit synthetic assumption disclaimer
    """
    downtime_hours = 2.0 + 0.5 * float(row["failure_history_count"])
    energy_loss_mwh = round(float(row["peak_load_mw"]) * downtime_hours, 2)
    economic_impact = round(
        float(row["customers_affected"]) * downtime_hours * _COST_PER_CUSTOMER_HOUR_USD, 2
    )

    return {
        "asset_id":                       str(row["asset_id"]),
        "customers_affected":             int(row["customers_affected"]),
        "critical_facilities":            int(row["critical_facilities"]),
        "estimated_downtime_hours":       round(downtime_hours, 1),
        "estimated_energy_loss_mwh":      energy_loss_mwh,
        "estimated_economic_impact_usd":  economic_impact,
        "_note":                          _IMPACT_NOTE,
    }


# ---------------------------------------------------------------------------
# Recommendations
# ---------------------------------------------------------------------------

def get_recommendations(row: pd.Series) -> list[str]:
    """
    Return a list of preventive action recommendations for a single asset.
    Multiple rules can fire simultaneously.
    Always returns at least one recommendation for HIGH and CRITICAL assets.
    """
    recs: list[str] = []

    eq_label  = str(row.get("equipment_risk_label", ""))
    out_label = str(row.get("outage_risk_label", ""))

    if eq_label == "CRITICAL":
        recs.append("Immediate shutdown and emergency inspection required")

    if float(row["load_pct"]) > 95:
        recs.append("Reduce load — asset is operating above rated capacity")

    if float(row["temp_c"]) > 80:
        recs.append("Thermal inspection required — overheating detected")

    if int(row["last_maintenance_days"]) > 365:
        recs.append("Schedule preventive maintenance — overdue by more than one year")

    if int(row["failure_history_count"]) >= 5:
        recs.append("Review asset lifecycle — repeated failure history")

    if int(row["weather_severity"]) >= 2:
        recs.append("Deploy weather hardening measures")

    if int(row["age_years"]) > 30:
        recs.append("Asset approaching end of operational life — plan replacement")

    if int(row["asset_criticality"]) == 3 and out_label in ("HIGH", "CRITICAL"):
        recs.append(
            "Priority response required — critical infrastructure asset at elevated outage risk"
        )

    # Ensure a baseline recommendation is always present
    if not recs:
        recs.append("Continue routine monitoring — no immediate action required")

    return recs


# ---------------------------------------------------------------------------
# GridGuard Operations Copilot (rule-based stub)
# ---------------------------------------------------------------------------

def copilot_answer(question: str, df: pd.DataFrame) -> str:
    """
    Return a natural-language answer based on pattern matching against
    the live equipment DataFrame.

    This is a rule-based stub. It is explicitly NOT powered by IBM Bob or
    any external AI at runtime. Label for display:
        "GridGuard Operations Copilot — rule-based MVP,
         designed for future IBM AI integration"

    Recognised patterns (case-insensitive):
        "critical" / "worst"       → top-3 CRITICAL equipment-risk assets
        "high risk"                → HIGH+CRITICAL count and worst zone
        "recommend" / "what should"→ recommendations for top or named asset
        "outage"                   → zone with highest average outage risk
        "impact"                   → asset with highest estimated economic impact
        fallback                   → portfolio summary
    """
    q = question.lower().strip()

    # Guard: ensure scoring columns exist
    if "equipment_risk_score" not in df.columns:
        return (
            "GridGuard AI is still initialising risk data. "
            "Please try again in a moment."
        )

    total = len(df)
    high_critical = int(
        df["equipment_risk_label"].isin(["HIGH", "CRITICAL"]).sum()
    )

    # Pattern: outage (checked before "worst" to avoid "worst outage risk" misfiring)
    if "outage" in q:
        zone_avg = df.groupby("zone")["outage_risk_score"].mean()
        worst_zone = zone_avg.idxmax()
        worst_score = zone_avg.max()
        return (
            f"The zone with the highest average outage risk is {worst_zone} "
            f"(average outage risk score: {worst_score:.1f}/100). "
            f"GridGuard AI recommends prioritising preventive action in this zone."
        )

    # Pattern: critical / worst
    if any(kw in q for kw in ("critical", "worst")):
        crit = df[df["equipment_risk_label"] == "CRITICAL"].nlargest(
            3, "equipment_risk_score"
        )
        if crit.empty:
            return (
                f"Good news — none of the {total} monitored assets currently "
                "score CRITICAL on equipment failure risk."
            )
        lines = [
            f"{r['name']} ({r['zone']}) — equipment risk score {r['equipment_risk_score']:.1f}/100"
            for _, r in crit.iterrows()
        ]
        return (
            f"The {len(crit)} highest-risk assets at CRITICAL level are:\n"
            + "\n".join(f"  {i+1}. {l}" for i, l in enumerate(lines))
        )

    # Pattern: high risk
    if "high risk" in q:
        zone_counts = (
            df[df["equipment_risk_label"].isin(["HIGH", "CRITICAL"])]
            .groupby("zone")
            .size()
        )
        worst_zone = zone_counts.idxmax() if not zone_counts.empty else "N/A"
        return (
            f"GridGuard AI has identified {high_critical} of {total} assets "
            f"at HIGH or CRITICAL equipment failure risk. "
            f"The zone with the most at-risk assets is {worst_zone} "
            f"({zone_counts.get(worst_zone, 0)} assets)."
        )

    # Pattern: recommend / what should
    if any(kw in q for kw in ("recommend", "what should")):
        # Try to find a named asset in the question
        match = df[df["name"].str.lower().apply(lambda n: n in q)]
        if match.empty:
            # Fall back to highest equipment risk asset
            match = df.nlargest(1, "equipment_risk_score")
        row = match.iloc[0]
        recs = get_recommendations(row)
        return (
            f"For {row['name']} ({row['zone']}, equipment risk {row['equipment_risk_score']:.1f}/100):\n"
            + "\n".join(f"  • {r}" for r in recs)
        )

    # Pattern: impact
    if "impact" in q:
        impacts = df.apply(
            lambda r: float(r["customers_affected"])
            * (2.0 + 0.5 * float(r["failure_history_count"]))
            * _COST_PER_CUSTOMER_HOUR_USD,
            axis=1,
        )
        idx = impacts.idxmax()
        row = df.loc[idx]
        est = impacts[idx]
        return (
            f"The asset with the highest estimated economic impact is "
            f"{row['name']} ({row['zone']}), serving {int(row['customers_affected']):,} customers "
            f"with an estimated outage cost of ${est:,.0f} "
            f"(synthetic demo estimate — $4.50/customer/hour assumption)."
        )

    # Fallback — portfolio summary
    crit_count = int((df["equipment_risk_label"] == "CRITICAL").sum())
    out_crit   = int((df["outage_risk_label"] == "CRITICAL").sum())
    return (
        f"GridGuard AI has analysed {total} grid assets. "
        f"{high_critical} are at HIGH or CRITICAL equipment failure risk "
        f"({crit_count} CRITICAL). "
        f"{out_crit} assets are at CRITICAL outage risk. "
        "Ask me about critical assets, high-risk zones, outage risk, "
        "impact estimates, or recommendations for a specific asset."
    )
