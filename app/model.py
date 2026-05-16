import pickle
import os
import numpy as np
import joblib

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

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

model_path = os.path.join(BASE_DIR, 'credit_model.pkl')
scaler_path = os.path.join(BASE_DIR, 'scaler.pkl')

model = joblib.load(model_path)
scaler = joblib.load(scaler_path)

def predict_credit_score(duration, amount, installment_rate, age, existing_credits):

    features = np.array([[duration, amount, installment_rate, age, existing_credits]])

    scaled = scaler.transform(features)

    # Probability of GOOD credit
    prob_good = model.predict_proba(scaled)[0][1]

    # Probability of default
    pd = 1 - prob_good

    # Convert to score
    score = round(prob_good * 100, 2)

    # Risk categories
    if pd >= 0.6:
        risk = "High"
    elif pd >= 0.3:
        risk = "Medium"
    else:
        risk = "Low"

    # Banking assumptions
    lgd = 0.45
    ead = amount

    # Expected Loss
    expected_loss = round(pd * lgd * ead, 2)

    return {
        "score": score,
        "risk": risk,
        "pd": round(pd, 4),
        "lgd": lgd,
        "ead": ead,
        "expected_loss": expected_loss
    }


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