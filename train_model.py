import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
import pickle

# --- CREATE SYNTHETIC DATA (for now) ---
np.random.seed(42)

n = 1000

data = pd.DataFrame({
    "income": np.random.randint(1000, 6000, n),
    "expenses": np.random.randint(500, 4000, n),
    "savings": np.random.randint(0, 5000, n),
    "missed": np.random.randint(0, 5, n)
})

# --- CREATE TARGET (default or not) ---
# Higher risk if:
# - high expenses
# - low savings
# - more missed payments

data["default"] = (
    (data["expenses"] > data["income"] * 0.7) |
    (data["savings"] < 500) |
    (data["missed"] >= 2)
).astype(int)

# --- FEATURES / TARGET ---
X = data[["income", "expenses", "savings", "missed"]]
y = data["default"]

# --- TRAIN MODEL ---
model = LogisticRegression()
model.fit(X, y)

# --- SAVE MODEL ---
with open("model.pkl", "wb") as f:
    pickle.dump(model, f)

print("Model trained and saved!")