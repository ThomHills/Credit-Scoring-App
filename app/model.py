import pickle
import numpy as np
import os

# --- LOAD MODEL SAFELY ---
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model.pkl")

try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    model = None
    print("Error loading model:", e)


# --- PREDICTION FUNCTION ---
def predict_credit_score(income, expenses, savings, missed):
    """
    Predicts:
    - Probability of Default (PD)
    - Credit Score (0–100)
    - Risk Category (Low / Medium / High)
    """

    if model is None:
        return {
            "error": "Model not loaded"
        }

    # --- INPUT FORMAT ---
    X = np.array([[income, expenses, savings, missed]])

    # --- PREDICTION ---
    prob_default = model.predict_proba(X)[0][1]  # probability of default

    # --- SCORE (inverse of risk) ---
    score = (1 - prob_default) * 100

    # --- RISK CLASSIFICATION ---
    if prob_default > 0.6:
        risk = "High"
    elif prob_default > 0.3:
        risk = "Medium"
    else:
        risk = "Low"

    return {
        "score": round(score, 2),
        "risk": risk,
        "prob_default": round(prob_default, 3)
    }