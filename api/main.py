import os
from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()

# Load trained ML model
_model_path = os.path.join(os.path.dirname(__file__), "..", "models", "water_model.pkl")
model = joblib.load(_model_path)

# Store last sensor readings
reading_history = []

# ---------- SAFETY SCORE ----------

def calculate_safety_score(ph: float, tds: float, conductivity: float, turbidity: float):


    score = 100

    if turbidity > 5:
        score -= 30

    if tds > 500:
        score -= 25

    if ph < 6.5 or ph > 8.5:
        score -= 20

    if conductivity > 600:
        score -= 15

    return max(score, 0)


# ---------- CAUSE DETECTION ----------

def detect_causes(ph: float, tds: float, conductivity: float, turbidity: float):


    causes = []

    if turbidity > 5:
        causes.append("High turbidity detected (possible sediment contamination or soil runoff)")

    if tds > 500:
        causes.append("High TDS detected (possible industrial waste or mineral contamination)")

    if ph < 6.5:
        causes.append("Water is acidic (possible chemical contamination or acid rain)")

    if ph > 8.5:
        causes.append("Water is alkaline (possible waste discharge or mineral imbalance)")

    if conductivity > 600:
        causes.append("High conductivity detected (excess dissolved salts in water)")

    if not causes:
        causes.append("No major contamination indicators detected")

    return causes


# ---------- RECOMMENDATIONS ----------

def recommend_actions(ph: float, tds: float, conductivity: float, turbidity: float):


    actions = []

    if turbidity > 5:
        actions.append("Use sediment filtration or allow water to settle before use")

    if tds > 500:
        actions.append("Install reverse osmosis (RO) purification system")

    if ph < 6.5 or ph > 8.5:
        actions.append("Test water for chemical pollutants and adjust pH levels")

    if conductivity > 600:
        actions.append("Investigate possible industrial discharge near the water source")

    if not actions:
        actions.append("Water quality appears stable. Continue regular monitoring.")

    return actions
    

# ---------- RISK LEVEL ----------

def risk_level(score: int):


    if score >= 80:
        return "Low"

    elif score >= 50:
        return "Moderate"

    else:
        return "High"

def future_risk_analysis(ph, tds, conductivity, turbidity):

    global reading_history

    reading_history.append({
        "ph": ph,
        "tds": tds,
        "conductivity": conductivity,
        "turbidity": turbidity
    })

    # keep only last 5 readings
    if len(reading_history) > 5:
        reading_history.pop(0)

    if len(reading_history) < 3:
        return "Insufficient data for prediction"

    turbidity_values = [r["turbidity"] for r in reading_history]

    if turbidity_values[-1] > turbidity_values[0] + 2:
        return "Turbidity rising rapidly – contamination risk increasing"

    tds_values = [r["tds"] for r in reading_history]

    if tds_values[-1] > tds_values[0] + 100:
        return "TDS increasing – possible chemical contamination developing"

    return "Water parameters stable"

# ---------- HOME ROUTE ----------

@app.get("/")
def home():
    return {"message": "JalRakshak AI running"}

# ---------- AI PREDICTION ----------

@app.post("/predict")
def predict_water(ph: float, tds: float, conductivity: float, turbidity: float):


    data = np.array([[ph, tds, conductivity, turbidity]])

    prediction = model.predict(data)[0]

    # Prediction confidence
    prob = model.predict_proba(data)
    confidence = round(max(prob[0]) * 100, 2)

    # Safety score
    score = calculate_safety_score(ph, tds, conductivity, turbidity)

    # Cause detection
    causes = detect_causes(ph, tds, conductivity, turbidity)

    # Recommended actions
    actions = recommend_actions(ph, tds, conductivity, turbidity)

    # Risk level
    risk = risk_level(score)

    if score < 50:
        status = "Unsafe"
    elif prediction == 0:
        status = "Unsafe"
    else:
        status = "Safe"
    

    future_risk = future_risk_analysis(ph, tds, conductivity, turbidity)

    return {
        "water_status": status,
        "confidence": f"{confidence}%",
        "safety_score": score,
        "risk_level": risk,
        "possible_causes": causes,
        "recommended_actions": actions,
        "future_risk": future_risk
    }
    
