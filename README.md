# 🚀 GridGuard AI




---

## 👥 Team

| Field | Value |
|---|---|
| **Team Name** | VertexAI |
| **Track** | AI |
| **Team Lead** | Vaidehi Patel — 25cs081@charusat.edu.in|
| **Members** | Devanshi Patel, Aadya Raval, Durva Naik |

---

## 🎯 Problem Statement


Power transformers and substation equipment can develop failure conditions that lead to costly outages and service disruptions. GridGuard AI combines equipment health data, weather conditions, and historical failure/outage information to identify high-risk equipment and outage-prone zones before failures occur.
---

## 💡 Solution


 ## **GridGuard AI is a predictive grid-maintenance dashboard that calculates equipment and outage risk scores, ranks vulnerable assets by priority, estimates potential impact, and provides actionable maintenance recommendations. An Operations Copilot helps users query the risk information and understand which assets or areas require attention.**

---

## ✨ Key Features

### **Feature 1:**  
### Grid Overview — Displays total assets, critical equipment, high-risk assets, outage risk, and average equipment score.

### **Feature 2:** 
### Equipment Failure Risk — Calculates asset risk using age, load, temperature, maintenance, failure history, and weather factors.

### **Feature 3:** 
### Outage Risk Analysis — Identifies potential outage risks using equipment risk, load, weather, outage history, and asset criticality.

### **Feature 4:** 
### Vulnerable Asset Ranking — Ranks the Top 10 highest-risk assets for quick operator attention.

### **Feature 5:** 
### Impact Analysis — Estimates customers affected, critical facilities, downtime, energy loss, and economic impact.

### **Feature 6:** 
### Preventive Recommendations — Provides prioritized actions such as inspection, load reduction, maintenance, and replacement planning.

### **Feature 7:** 
### Outage Risk by Zone — Highlights high-risk grid zones and their overall outage risk levels.

### **Feature 8:** 
### Grid Operations Copilot — A rule-based assistant for queries about critical assets, outage risks, recommendations, and impact.

---

## 🛠️ Tech Stack

| Category | Technologies |
|---|---|
| **Languages** | Python, JavaScript, HTML, CSS |
| **Frameworks** | FastAPI |
| **IBM Technologies** | IBM Bob |
| **Databases** | In-memory processing |
| **Other** | Pandas, NumPy, Uvicorn, Git, GitHub |

---

## 📁 Repository Structure

```text
├── src/                  # Application source code
│   └── backend/          # FastAPI backend and dashboard
│       ├── data/         # Equipment dataset
│       ├── static/       # Frontend files
│       │   ├── index.html
│       │   ├── app.js
│       │   └── style.css
│       ├── main.py       # FastAPI application
│       ├── risk_engine.py # Risk scoring and recommendations
│       └── requirements.txt # Python dependencies
├── docs/                 # Project documentation
├── demo/                 # Demo artifacts
├── presentation/         # Hackathon presentation
└── submission.yaml       # Submission metadata
```

## ⚡ How to Run

### 💻 Run Locally

```bash
# 1. Clone the repo
git clone https://github.com/VaidehiPatel2107/bob-ai-hackathon-VertexAI.git
cd bob-ai-hackathon-VertexAI

# 2. Install dependencies
python -m pip install -r src/backend/requirements.txt

# 3. Run the project
cd src/backend
py -m uvicorn main:app --reload --port 8001
```

The dashboard will be available at `http://127.0.0.1:8001`.
## 🖥️ Demo

| Artifact | Link |
|---|---|
| 📹 Demo Video | [See demo/demo-video-link.txt](demo/demo-video-link.txt) |
| 🌐 Live Demo | [See demo/live-demo-url.txt](https://gridguard-ai-h8ok.onrender.com/) |
| 🖼️ Screenshots | [See demo/screenshots/](demo/screenshots/) |
| 📊 Presentation | [See presentation/slides.pdf](presentation/) |

---

## ⚠️ Known Limitations


### - **Risk Prediction:** Uses a weighted rule-based scoring approach instead of a trained machine-learning model.
### - **Data:** Uses a static demonstration dataset rather than live grid sensor and weather data.
### - **AI Copilot:** Currently rule-based and designed for future generative AI integration.

---

## 🏅 What We're Most Proud Of

### We are most proud of building a practical grid intelligence platform that brings **equipment failure risk, outage risk, impact analysis, and preventive recommendations** together in one dashboard. It helps operators quickly identify the most vulnerable assets and prioritize maintenance before failures become major outages.
