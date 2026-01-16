import logging

import mlflow
import mlflow.sklearn
import numpy as np
import joblib
from pathlib import Path

from fastapi import logger

from app.mlflow_client import setup_mlflow
from app.models.severity_model import load_model, predict
from typing import List

logger = logging.getLogger(__name__)

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

def predict(model, features: List[float]) -> float:
    features_np = np.array(features, dtype=float).reshape(1, -1)

    # Supports sklearn classifiers or regressors
    if hasattr(model, "predict_proba"):
        return float(model.predict_proba(features_np)[0][1])

    return float(model.predict(features_np)[0])


def log_and_register(features: list[float]) -> float:
    """
    Runs inference using a pre-trained model,
    logs the MLflow run, and registers the model.
    """
    model = get_model()
    features_np = np.array(features).reshape(1, -1)

    severity_score = float(model.predict_proba(features_np)[0][1])

    try:
        setup_mlflow()
        with mlflow.start_run(run_name="severity_score_inference"):
            mlflow.log_param("model_name", MODEL_NAME)
            mlflow.log_param("feature_count", len(features))
            mlflow.log_metric("severity_score", severity_score)
    except Exception as e:
        logger.warning(f"MLflow unavailable, continuing without logging: {e}")

    return severity_score

def score_patient(features: List[float]) -> float:
    if not isinstance(features, list):
        raise ValueError("features must be a list")

    if len(features) != EXPECTED_FEATURES:
        raise ValueError(
            f"Expected {EXPECTED_FEATURES} features, got {len(features)}"
        )

    if any(f is None for f in features):
        raise ValueError("features contain None")

    model = load_model()
    severity_score = predict(model, features)

    # Optional MLflow logging
    try:
        setup_mlflow()
        with mlflow.start_run(run_name="patient_score_inference"):
            mlflow.log_metric("severity_score", severity_score)
    except Exception as e:
        logger.warning(f"MLflow logging skipped: {e}")

    return max(0.0, min(1.0, float(severity_score)))


def is_terminal(severity_score: float) -> bool:
    return severity_score >= 0.85