"""
Flood Early Warning — Machine Learning (Humanised)
-------------------------------------------------
Learn how to train a simple model that predicts flood risk
using rainfall, soil moisture, and river level. The dataset
here is synthetic so you can run it anywhere; swap with real
data when ready.
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import joblib, os

def make_demo_data(n_rows: int = 2000, seed: int = 42) -> pd.DataFrame:
    """Create a clean, synthetic dataset with intuitive columns."""
    rng = np.random.default_rng(seed)
    rainfall_mm = rng.gamma(shape=2.5, scale=10, size=n_rows)      # mm/day
    soil_moisture = rng.uniform(0.1, 0.6, size=n_rows)            # fraction (0–1)
    river_level_m = rng.normal(2.0, 0.7, size=n_rows)             # metres
    # Simple antecedent rainfall index (average of last few days, scaled)
    antecedent = np.convolve(rainfall_mm, np.ones(5)/5, mode="same")/50.0

    # Create a "flood probability" then draw 0/1 labels from it
    logits = 0.06*rainfall_mm + 3*soil_moisture + 0.9*river_level_m + 2.5*antecedent - 5
    prob = 1/(1+np.exp(-logits))
    flood = (rng.uniform(0, 1, size=n_rows) < prob).astype(int)

    return pd.DataFrame({
        "rainfall_mm": rainfall_mm,
        "soil_moisture": soil_moisture,
        "river_level_m": river_level_m,
        "antecedent_idx": antecedent,
        "flood": flood
    })

def main():
    print("\nSTEP 1 ▸ Create or load data..." )
    data = make_demo_data()

    # Separate features and label
    X = data[["rainfall_mm", "soil_moisture", "river_level_m", "antecedent_idx"]]
    y = data["flood"]

    print("STEP 2 ▸ Train/test split..." )
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print("STEP 3 ▸ Scale features (common in ML)..." )
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    print("STEP 4 ▸ Train RandomForest model..." )
    model = RandomForestClassifier(n_estimators=300, max_depth=8, class_weight="balanced", random_state=42)
    model.fit(X_train_s, y_train)

    print("STEP 5 ▸ Evaluate model...\n" )
    preds = model.predict(X_test_s)
    print(confusion_matrix(y_test, preds))
    print(classification_report(y_test, preds, digits=3))

    print("STEP 6 ▸ Save model for later use..." )
    os.makedirs("artifacts", exist_ok=True)
    joblib.dump(model, "artifacts/model.joblib")
    joblib.dump(scaler, "artifacts/scaler.joblib")
    print("Saved: artifacts/model.joblib and artifacts/scaler.joblib" )

    print("STEP 7 ▸ Try a single prediction..." )
    example = pd.DataFrame([{
        "rainfall_mm": 55, "soil_moisture": 0.45, "river_level_m": 2.8, "antecedent_idx": 0.8
    }])
    proba = model.predict_proba(scaler.transform(example))[0,1]
    print(f"Example conditions: {example.to_dict(orient='records')[0]}" )
    print(f"Flood probability ≈ {proba:.2f}" )
    print("⚠️ WARNING" if proba>0.5 else "✅ Likely Safe") 

if __name__ == "__main__":
    main()
