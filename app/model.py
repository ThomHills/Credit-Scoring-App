import pickle
import os
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# LOAD MODEL
try:
    with open(os.path.join(BASE_DIR, "../model.pkl"), "rb") as f:
        model = pickle.load(f)

    with open(os.path.join(BASE_DIR, "../scaler.pkl"), "rb") as f:
        scaler = pickle.load(f)

except:
    model = None
    scaler = None


# -----------------------
# PREDICTION
# -----------------------
def predict_credit_score(duration, amount, installment_rate, age, existing_credits):

    if model is None or scaler is None:
        return {"error": "Model not loaded"}

    try:
        X = np.array([[
            duration,
            amount,
            installment_rate,
            age,
            existing_credits
        ]])

        X_scaled = scaler.transform(X)

        prob_default = model.predict_proba(X_scaled)[0][1]

        score = round((1 - prob_default) * 100, 2)

        if score > 70:
            risk = "Low"
        elif score > 40:
            risk = "Medium"
        else:
            risk = "High"

        return {
            "score": score,
            "risk": risk,
            "prob_default": round(prob_default, 3)
        }

    except Exception as e:
        return {"error": str(e)}


# -----------------------
# FEATURE IMPORTANCE
# -----------------------
def get_feature_importance():
    try:
        coefs = model.coef_[0]
        names = ["duration","amount","installment_rate","age","existing_credits"]
        return dict(zip(names, coefs))
    except:
        return {}