import mlflow
import mlflow.sklearn
import numpy as np
import joblib
from pathlib import Path

from app.mlflow_client import setup_mlflow
from app.models.severity_model import load_model, predict
from typing import List

MODEL_NAME = "SeverityScoringModel"

ARTIFACT_DIR = Path("artifacts")
MODEL_FILE = ARTIFACT_DIR / "severity_model.joblib"
EXPECTED_FEATURES = 8

def get_model():
    return load_model()

def _load_model():
    if not MODEL_FILE.exists():
        raise FileNotFoundError(
            f"Model file not found at {MODEL_FILE}. "
            "Run create_severity_model.py first."
        )
    return joblib.load(MODEL_FILE)


def log_and_register(features: list[float]) -> float:
    """
    Runs inference using a pre-trained model,
    logs the MLflow run, and registers the model.
    """
    setup_mlflow()
    model = _load_model()
    features_np = np.array(features).reshape(1, -1)

    with mlflow.start_run(run_name="severity_score_inference"):

        severity_score = float(model.predict_proba(features_np)[0][1])

        # ---- Params ----
        mlflow.log_param("model_name", MODEL_NAME)
        mlflow.log_param("feature_count", len(features))

        # ---- Metrics ----
        mlflow.log_metric("severity_score", severity_score)

        # ---- Model Artifact + Registry ----
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=MODEL_NAME
        )

        return severity_score

def score_patient(features: List[float]) -> float:
    """
    Compute a severity score for a patient based on features.

    Args:
        features (List[float]): Patient feature vector.

    Returns:
        float: Severity score between 0.0 (low) and 1.0 (high).
    """
    if not isinstance(features, list):
        raise ValueError("features must be a list")

    if len(features) != EXPECTED_FEATURES:
        raise ValueError(
            f"Expected {EXPECTED_FEATURES} features, got {len(features)}"
        )

    if any(f is None for f in features):
        raise ValueError("features contain None")

    # Use ML model to compute probability of critical/terminal state
    model = get_model()
    score = predict(model, features)

    # Optional: clamp between 0 and 1
    score = max(0.0, min(1.0, score))
    return score


def is_terminal(severity_score: float) -> bool:
    """
    Determine whether the patient is considered terminal (critical).

    Args:
        severity_score (float): Severity score from score_patient.

    Returns:
        bool: True if patient is terminal, False otherwise.
    """
    # Example threshold; adjust based on clinical model calibration
    TERMINAL_THRESHOLD = 0.85
    return severity_score >= TERMINAL_THRESHOLD