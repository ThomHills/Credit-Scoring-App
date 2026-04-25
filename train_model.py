import pandas as pd
import numpy as np
import pickle

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, auc

# -----------------------
# LOAD DATA
# -----------------------
cols = [
    "status","duration","credit_history","purpose","amount",
    "savings","employment","installment_rate","personal_status",
    "other_debtors","residence","property","age",
    "other_installment","housing","existing_credits",
    "job","people_liable","telephone","foreign_worker","target"
]

df = pd.read_csv("german.data", sep=" ", names=cols)

# TARGET: 1 = bad, 0 = good
df["target"] = df["target"].apply(lambda x: 1 if x == 2 else 0)

# -----------------------
# SIMPLE FEATURE SELECTION
# -----------------------
X = df[[
    "duration",
    "amount",
    "installment_rate",
    "age",
    "existing_credits"
]]

y = df["target"]

# -----------------------
# SPLIT
# -----------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# -----------------------
# SCALE
# -----------------------
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# -----------------------
# MODEL
# -----------------------
model = LogisticRegression(max_iter=2000)
model.fit(X_train, y_train)

# -----------------------
# ROC
# -----------------------
y_probs = model.predict_proba(X_test)[:, 1]

fpr, tpr, _ = roc_curve(y_test, y_probs)
roc_auc = auc(fpr, tpr)

print("AUC:", roc_auc)

# -----------------------
# SAVE
# -----------------------
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("scaler.pkl", "wb") as f:
    pickle.dump(scaler, f)

with open("roc_data.pkl", "wb") as f:
    pickle.dump({
        "fpr": fpr.tolist(),
        "tpr": tpr.tolist(),
        "auc": roc_auc
    }, f)

print("Model + ROC saved!")