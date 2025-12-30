import joblib
import numpy as np
from sklearn.linear_model import LogisticRegression

MODEL_PATH = "artifacts/severity_model.joblib"
EXPECTED_FEATURES = 8

def train_dummy_model():
    X = np.random.rand(200, EXPECTED_FEATURES)
    y = (X.sum(axis=1) > (EXPECTED_FEATURES / 2)).astype(int)
    model = LogisticRegression()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)
    return model

def load_model():
    return joblib.load(MODEL_PATH)

def predict(model, features):
    return float(model.predict_proba([features])[0][1])