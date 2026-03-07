# JalRakshak AI — Intelligent Water Quality Monitoring System

> **JalRakshak** (जलरक्षक) means *Water Guardian* in Sanskrit/Hindi. This system uses Machine Learning to predict water safety, detect contamination causes, recommend actions, and forecast future water quality trends — all in real time.

---

## Table of Contents

- [Overview](#overview)
- [How the Model Works](#how-the-model-works)
- [Features](#features)
- [Project Structure](#project-structure)
- [API Endpoints](#api-endpoints)
- [Installation & Setup](#installation--setup)
- [Running the Project](#running-the-project)
- [Example API Response](#example-api-response)
- [Dataset](#dataset)

---

## Overview

JalRakshak AI ingests real-time sensor readings from water sources (pH, TDS, Conductivity, Turbidity), runs them through a trained Machine Learning model, and returns:

- A **safe/unsafe classification** of the water
- A **safety score** (0–100)
- A **risk level** (Low / Moderate / High)
- **Possible contamination causes**
- **Recommended remediation actions**
- A **future risk trend** based on rolling sensor history

---

## How the Model Works

### 1. Dataset
The model is trained on the [Water Potability dataset](https://www.kaggle.com/datasets/adityakadiwal/water-potability), which contains physicochemical water quality measurements. Four sensor-friendly features are extracted:

| Feature | Original Column | Description |
|---|---|---|
| `ph` | `ph` | Acidity/alkalinity of water (ideal: 6.5–8.5) |
| `tds` | `Solids` | Total Dissolved Solids in mg/L (safe: < 500) |
| `conductivity` | `Conductivity` | Electrical conductivity in μS/cm (safe: < 600) |
| `turbidity` | `Turbidity` | Water clarity in NTU (safe: < 5) |

Target label: `Potability` (1 = potable/safe, 0 = not potable/unsafe)

### 2. Preprocessing (`utils/preprocess.py`)
- Selects the four sensor features and the `Potability` label
- Renames columns to lowercase, consistent names
- Fills missing values with the **column mean** (mean imputation)

### 3. Model Training (`models/train_model.py`)
- Algorithm: **Random Forest Classifier** (`n_estimators=200`)
- Split: 80% training / 20% testing (`random_state=42`)
- Saved as `models/water_model.pkl` using `joblib`

Random Forest was chosen because:
- It handles non-linear relationships between water quality parameters
- Robust to outliers (common in sensor data)
- Natively provides **class probability estimates** for confidence scoring

### 4. Prediction Pipeline (`api/main.py`)
When a `/predict` request is received, the following steps run:

```
Sensor Input (ph, tds, conductivity, turbidity)
        │
        ▼
   ML Model Prediction ──► potable / not potable + confidence %
        │
        ▼
   Safety Score Calculator (rule-based, 0–100)
        │
        ▼
   Cause Detector (identifies which parameters are out of range)
        │
        ▼
   Recommendation Engine (suggests remediation actions)
        │
        ▼
   Risk Level Classifier (Low / Moderate / High)
        │
        ▼
   Future Risk Analyzer (trend detection over last 5 readings)
        │
        ▼
   JSON Response
```

### 5. Safety Score Logic
The score starts at 100 and deductions are applied based on threshold breaches:

| Parameter | Condition | Penalty |
|---|---|---|
| Turbidity | > 5 NTU | −30 |
| TDS | > 500 mg/L | −25 |
| pH | < 6.5 or > 8.5 | −20 |
| Conductivity | > 600 μS/cm | −15 |

Score is clamped to a minimum of 0. The final water status uses **both** the ML prediction and the safety score — if either indicates unsafe, the water is flagged as **Unsafe**.

### 6. Future Risk Analysis
A rolling window of the **last 5 sensor readings** is kept in memory. Trend rules:
- If turbidity increased by more than 2 NTU → contamination risk increasing
- If TDS increased by more than 100 mg/L → possible chemical contamination developing
- Otherwise → parameters stable

---

## Features

- Real-time water quality prediction via REST API
- ML confidence score per prediction
- Rule-based safety scoring (complements the ML model)
- Contamination cause detection with human-readable descriptions
- Actionable remediation recommendations
- Trend-based future risk forecasting
- Sensor simulator for testing without physical hardware

---

## Project Structure

```
JALRAKSHAK-AI/
├── api/
│   └── main.py              # FastAPI app — prediction endpoint & logic
├── data/
│   └── water_potability.csv # Training dataset
├── models/
│   ├── train_model.py       # Model training script
│   └── water_model.pkl      # Trained model (generated after training)
├── utils/
│   ├── __init__.py
│   └── preprocess.py        # Data loading and preprocessing
├── sensor_simulator.py      # Simulates sensor readings hitting the API
├── requirements.txt         # Python dependencies
└── README.md
```

---

## API Endpoints

### `GET /`
Health check.

**Response:**
```json
{ "message": "JalRakshak AI running" }
```

### `POST /predict`
Predict water safety from sensor parameters.

**Query Parameters:**

| Parameter | Type | Description |
|---|---|---|
| `ph` | float | pH value of the water |
| `tds` | float | Total Dissolved Solids (mg/L) |
| `conductivity` | float | Electrical conductivity (μS/cm) |
| `turbidity` | float | Turbidity (NTU) |

---

## Installation & Setup

```bash
# 1. Clone the repository
git clone <repo-url>
cd JALRAKSHAK-AI

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the model (generates models/water_model.pkl)
python models/train_model.py
```

---

## Running the Project

**Start the API server:**
```bash
uvicorn api.main:app --reload
```
The API will be available at `http://127.0.0.1:8000`

**Run the sensor simulator** (in a separate terminal, while the API is running):
```bash
python sensor_simulator.py
```
The simulator sends random sensor readings to the API every 5 seconds and prints the JSON response.

**Interactive API docs:**  
Visit `http://127.0.0.1:8000/docs` for the auto-generated Swagger UI.

---

## Example API Response

```json
{
  "water_status": "Unsafe",
  "confidence": "87.5%",
  "safety_score": 45,
  "risk_level": "High",
  "possible_causes": [
    "High turbidity detected (possible sediment contamination or soil runoff)",
    "High TDS detected (possible industrial waste or mineral contamination)"
  ],
  "recommended_actions": [
    "Use sediment filtration or allow water to settle before use",
    "Install reverse osmosis (RO) purification system"
  ],
  "future_risk": "Turbidity rising rapidly – contamination risk increasing"
}
```

---

## Dataset

- **Source:** [Kaggle — Water Potability](https://www.kaggle.com/datasets/adityakadiwal/water-potability)
- **Rows:** ~3,276 water samples
- **Label:** `Potability` — 1 (safe to drink) / 0 (not safe)
- **Missing values:** Handled via column mean imputation
