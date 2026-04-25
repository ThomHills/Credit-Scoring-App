import pandas as pd
import numpy as np
import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc

from sklearn.preprocessing import StandardScaler

np.random.seed(42)
n = 2000

# -------------------
# DATA
# -------------------
data = pd.DataFrame({
    "income": np.random.randint(1000, 6000, n),
    "expenses": np.random.randint(500, 4000, n),
    "savings": np.random.randint(0, 5000, n),
    "missed": np.random.randint(0, 5, n),

    "total_debt": np.random.randint(0, 10000, n),
    "credit_limit": np.random.randint(1000, 15000, n),
    "used_credit": np.random.randint(0, 10000, n),
    "late_payments": np.random.randint(0, 5, n),
    "credit_history": np.random.randint(1, 20, n),
    "new_accounts": np.random.randint(0, 5, n),
    "job_years": np.random.randint(0, 20, n),
    "residence_years": np.random.randint(0, 20, n)
})

# -------------------
# FEATURES
# -------------------
data["debt_to_income"] = data["total_debt"] / (data["income"] + 1)
data["credit_utilization"] = data["used_credit"] / (data["credit_limit"] + 1)

# -------------------
# TARGET
# -------------------
data["default"] = (
    (data["debt_to_income"] > 0.6) |
    (data["credit_utilization"] > 0.7) |
    (data["missed"] >= 2) |
    (data["late_payments"] >= 2) |
    (data["credit_history"] < 3) |
    (data["new_accounts"] > 3)
).astype(int)

X = data[[
    "income", "expenses", "savings", "missed",
    "debt_to_income", "credit_utilization",
    "late_payments", "credit_history",
    "new_accounts", "job_years", "residence_years"
]]

y = data["default"]

# -------------------
# TRAIN
# -------------------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3)

model = LogisticRegression(max_iter=2000)
model.fit(X_train, y_train)

# -------------------
# ROC + AUC
# -------------------
probs = model.predict_proba(X_test)[:, 1]

fpr, tpr, _ = roc_curve(y_test, probs)
roc_auc = auc(fpr, tpr)

print("AUC:", roc_auc)

# -------------------
# SAVE MODEL
# -------------------
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

# -------------------
# SAVE ROC DATA
# -------------------
with open("roc_data.pkl", "wb") as f:
    pickle.dump({
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "auc": roc_auc
    }, f)

with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)
print("Model and ROC saved!")