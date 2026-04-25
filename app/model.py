import pickle
import numpy as np
import os

# -----------------------
# PATH SETUP
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model_path = os.path.join(BASE_DIR, "..", "model.pkl")
scaler_path = os.path.join(BASE_DIR, "..", "scaler.pkl")

# -----------------------
# LOAD MODEL
# -----------------------
model = None
if os.path.exists(model_path):
    try:
        with open(model_path, "rb") as f:
            model = pickle.load(f)
        print("Model loaded successfully")
    except Exception as e:
        print("Error loading model:", e)

# -----------------------
# LOAD SCALER
# -----------------------
scaler = None
if os.path.exists(scaler_path):
    try:
        with open(scaler_path, "rb") as f:
            scaler = pickle.load(f)
        print("Scaler loaded successfully")
    except Exception as e:
        print("Error loading scaler:", e)

# -----------------------
# PREDICTION FUNCTION
# -----------------------
def predict_credit_score(
    income, expenses, savings, missed,
    total_debt, credit_limit, used_credit,
    late_payments, credit_history,
    new_accounts, job_years, residence_years
):
    try:
        # -----------------------
        # CHECK MODEL
        # -----------------------
        if model is None:
            return {"error": "Model not loaded"}

        # -----------------------
        # FEATURE ENGINEERING
        # -----------------------
        debt_to_income = total_debt / (income + 1)
        credit_utilization = used_credit / (credit_limit + 1)

        # -----------------------
        # FEATURE VECTOR
        # (MUST match training order exactly)
        # -----------------------
        X = np.array([[
            income,
            expenses,
            savings,
            missed,
            debt_to_income,
            credit_utilization,
            late_payments,
            credit_history,
            new_accounts,
            job_years,
            residence_years
        ]])

        # -----------------------
        # SCALE FEATURES
        # -----------------------
        if scaler is not None:
            X = scaler.transform(X)

        # -----------------------
        # PREDICT
        # -----------------------
        prob_default = model.predict_proba(X)[0][1]

        score = (1 - prob_default) * 100

        # -----------------------
        # RISK CLASSIFICATION
        # -----------------------
        if score > 70:
            risk = "Low"
        elif score > 40:
            risk = "Medium"
        else:
            risk = "High"

        return {
            "score": round(float(score), 2),
            "risk": risk,
            "prob_default": round(float(prob_default), 3)
        }

    except Exception as e:
        return {"error": str(e)}
    
def get_feature_importance():
    if model is None:
        return None

    feature_names = [
        "income", "expenses", "savings", "missed",
        "debt_to_income", "credit_utilization",
        "late_payments", "credit_history",
        "new_accounts", "job_years", "residence_years"
    ]

    coefs = model.coef_[0]

    importance = dict(zip(feature_names, coefs))

    return importance