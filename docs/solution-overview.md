# 💡 Solution Overview

## What We Built

**GridGuard AI** is a grid intelligence and risk analysis platform designed to help utility operators identify vulnerable grid equipment before it leads to a major power outage.

The system combines equipment condition, operating conditions, weather factors, maintenance history, failure history, outage history, and asset criticality to calculate two separate risk scores:

- **Equipment Failure Risk** — How likely an asset is to experience a failure.
- **Outage Risk** — How likely an asset is to contribute to a significant power outage.

The dashboard then ranks the most vulnerable assets, highlights high-risk grid zones, estimates the potential impact of failures, and provides prioritized preventive recommendations.

This gives operators a single view of **what is at risk, why it is at risk, what impact it could have, and what action should be considered first.**

## How It Works

1. **Equipment data is loaded** from a structured CSV dataset containing asset condition, load, temperature, maintenance, failure, weather, outage, and criticality information.

2. **Equipment risk is calculated** using multiple factors such as equipment age, load, temperature, maintenance history, failure history, and weather conditions.

3. **Outage risk is calculated separately** by combining equipment risk with load, weather, outage history, and asset criticality.

4. **Assets are ranked by risk** so operators can quickly identify the Top 10 most vulnerable assets.

5. **Grid zones are analyzed** to highlight areas with elevated outage risk.

6. **Potential impact is estimated** for selected assets, including affected customers, critical facilities, downtime, energy loss, and economic impact.

7. **Preventive recommendations are generated** based on the asset's risk factors, such as inspection, load reduction, maintenance, or replacement planning.

8. **The Grid Operations Copilot** provides rule-based responses to operator questions about critical assets, risks, recommendations, and impact analysis.

9. **The dashboard displays the results** through a centralized interface, allowing operators to understand grid risks and prioritize actions.

## Architecture Diagram

> See [`architecture.md`](architecture.md) for the detailed system architecture.

```mermaid
graph TD
    USER[User / Browser] --> DASH[GridGuard AI Dashboard]
    DASH -->|REST API| API[FastAPI Backend]
    API --> ENGINE[Risk Engine]
    ENGINE --> DATA[Equipment CSV Dataset]
    ENGINE --> EQUIP[Equipment Failure Risk]
    ENGINE --> OUTAGE[Outage Risk Analysis]
    ENGINE --> IMPACT[Impact Analysis]
    ENGINE --> RECOMMEND[Preventive Recommendations]
    API --> COPILOT[Grid Operations Copilot]
    EQUIP --> API
    OUTAGE --> API
    IMPACT --> API
    RECOMMEND --> API
    COPILOT --> API
    API -->|JSON Response| DASH

## Key Design Decisions

| **Decision** | **Rationale** |
|---|---|
| **Used a weighted risk-scoring approach** | Allows multiple equipment and operational factors to be combined into a single transparent risk score for the prototype. |
| **Separated equipment failure risk and outage risk** | Equipment failure probability and grid-level outage impact are different concepts, so they are evaluated separately. |
| **Combined multiple risk factors** | Age, load, temperature, maintenance history, failure history, weather, outage history, and criticality provide a broader view of asset risk than a single sensor or parameter. |
| **Ranked the Top 10 vulnerable assets** | Helps operators quickly identify the assets that require the most attention instead of manually reviewing the entire equipment list. |
| **Included impact analysis** | Shows the potential consequences of an asset failure, including affected customers, critical facilities, downtime, energy loss, and economic impact. |
| **Added preventive recommendations** | Converts risk results into practical actions such as inspection, load reduction, maintenance, and replacement planning. |
| **Used a lightweight CSV-based architecture** | Keeps the hackathon prototype simple, fast, and easy to demonstrate while leaving room for future live data integration. |
| **Designed the Copilot as a separate component** | Keeps the operator-assistance layer independent from the risk engine, making it easier to integrate generative AI in future versions. |

## IBM Technologies Used

- **IBM Bob:** Used as the development assistant throughout the project to support coding, debugging, documentation, architecture planning, and implementation of the GridGuard AI prototype.

### Future IBM Integration

The current prototype does **not** use IBM watsonx.ai as a runtime service. The Grid Operations Copilot is currently implemented using rule-based logic.

In a future version, **IBM watsonx.ai / Granite models** can be integrated to provide a generative AI Copilot capable of understanding natural-language operator queries, explaining risk factors, summarizing asset conditions, and generating more contextual maintenance recommendations.
