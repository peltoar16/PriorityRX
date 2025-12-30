import numpy as np
from sklearn.linear_model import LogisticRegression
import joblib
from pathlib import Path

# Path to store the model artifact
ARTIFACT_DIR = Path("artifacts")
ARTIFACT_DIR.mkdir(exist_ok=True)
MODEL_FILE = ARTIFACT_DIR / "severity_model.joblib"
EXPECTED_FEATURES = 8

# ---- Dummy training data ----
# Replace this with your real dataset later
X = np.random.rand(200, EXPECTED_FEATURES)        # 200 samples, 5 features
y = (X.sum(axis=1) > 2.5).astype(int)  # binary target

# ---- Train model ----
model = LogisticRegression()
model.fit(X, y)

# ---- Save the model ----
joblib.dump(model, MODEL_FILE)

print(f"Severity model saved to {MODEL_FILE}")