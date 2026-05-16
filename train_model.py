import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    roc_curve,
    auc,
    confusion_matrix,
    classification_report
)

# -----------------------
# LOAD DATA
# -----------------------
cols = [
    "status", "duration", "credit_history", "purpose", "amount",
    "savings", "employment", "installment_rate", "personal_status",
    "other_debtors", "residence", "property", "age",
    "other_installment", "housing", "existing_credits",
    "job", "people_liable", "telephone", "foreign_worker", "target"
]

print("Loading dataset...")

df = pd.read_csv(
    "german.data",
    sep=" ",
    names=cols
)

print("Dataset loaded successfully.")
print("Rows:", len(df))

# -----------------------
# TARGET
# 1 = BAD CREDIT (DEFAULT)
# 0 = GOOD CREDIT
# -----------------------
df["target"] = df["target"].apply(
    lambda x: 1 if x == 2 else 0
)

# -----------------------
# FEATURE SELECTION
# -----------------------
features = [
    "duration",
    "amount",
    "installment_rate",
    "age",
    "existing_credits"
]

X = df[features]
y = df["target"]

print("\nSelected Features:")
print(features)

# -----------------------
# TRAIN TEST SPLIT
# -----------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))

# -----------------------
# FEATURE SCALING
# -----------------------
print("\nScaling features...")

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# -----------------------
# MODEL TRAINING
# -----------------------
print("\nTraining Logistic Regression model...")

model = LogisticRegression(
    max_iter=2000,
    class_weight='balanced',
    random_state=42
)

model.fit(X_train_scaled, y_train)

print("Model training completed.")

# -----------------------
# PREDICTIONS
# -----------------------
y_probs = model.predict_proba(X_test_scaled)[:, 1]
y_pred = model.predict(X_test_scaled)

# -----------------------
# ROC / AUC
# -----------------------
fpr, tpr, _ = roc_curve(y_test, y_probs)
roc_auc = auc(fpr, tpr)

print("\nAUC Score:", round(roc_auc, 4))

# -----------------------
# CONFUSION MATRIX
# -----------------------
cm = confusion_matrix(y_test, y_pred)

print("\nConfusion Matrix:")
print(cm)

# -----------------------
# CLASSIFICATION REPORT
# -----------------------
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# -----------------------
# FEATURE IMPORTANCE
# -----------------------
print("\nFeature Importance (Model Coefficients):")

coefficients = pd.DataFrame({
    "Feature": features,
    "Coefficient": model.coef_[0]
})

coefficients["Importance"] = coefficients["Coefficient"].abs()

coefficients = coefficients.sort_values(
    by="Importance",
    ascending=False
)

print(coefficients)

# -----------------------
# SAVE MODEL
# -----------------------
print("\nSaving model files...")

joblib.dump(model, "credit_model.pkl")
joblib.dump(scaler, "scaler.pkl")

joblib.dump({
    "fpr": fpr.tolist(),
    "tpr": tpr.tolist(),
    "auc": roc_auc
}, "roc_data.pkl")

joblib.dump(
    coefficients.to_dict(orient="records"),
    "feature_importance.pkl"
)

print("\n===================================")
print("MODEL TRAINED SUCCESSFULLY")
print("Files saved:")
print("- credit_model.pkl")
print("- scaler.pkl")
print("- roc_data.pkl")
print("- feature_importance.pkl")
print("===================================")