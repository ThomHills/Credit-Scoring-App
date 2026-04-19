import pandas as pd
import numpy as np
import pickle

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, confusion_matrix, roc_curve, auc

# --- DATA ---
np.random.seed(42)
n = 1000

data = pd.DataFrame({
    "income": np.random.randint(1000, 6000, n),
    "expenses": np.random.randint(500, 4000, n),
    "savings": np.random.randint(0, 5000, n),
    "missed": np.random.randint(0, 5, n)
})

data["default"] = (
    (data["expenses"] > data["income"] * 0.7) |
    (data["savings"] < 500) |
    (data["missed"] >= 2)
).astype(int)

X = data[["income", "expenses", "savings", "missed"]]
y = data["default"]

# --- TRAIN TEST SPLIT ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)

# --- MODEL ---
model = LogisticRegression()
model.fit(X_train, y_train)

# --- PREDICTIONS ---
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# --- METRICS ---
accuracy = accuracy_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

fpr, tpr, _ = roc_curve(y_test, y_prob)
roc_auc = auc(fpr, tpr)

print("Accuracy:", accuracy)
print("Confusion Matrix:\n", cm)
print("AUC:", roc_auc)

# --- SAVE MODEL ---
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

# --- SAVE ROC DATA (for plotting in app) ---
roc_data = {
    "fpr": fpr.tolist(),
    "tpr": tpr.tolist(),
    "auc": roc_auc
}

with open("roc_data.pkl", "wb") as f:
    pickle.dump(roc_data, f)

print("Model and ROC data saved!")