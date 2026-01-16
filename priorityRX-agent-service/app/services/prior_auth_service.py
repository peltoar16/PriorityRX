import logging
from typing import List, Dict, Optional
import math
import random

import mlflow
import math
import random

from fastapi import logger

from app.mlflow_client import setup_mlflow

logger = logging.getLogger(__name__)

MODEL_NAME = "PriorAuthModel"
MODEL_VERSION = "pa-v1"
FEATURE_VERSION = "pa-fv-1"
PA_REQUIRED_THRESHOLD = 0.55


def assess_prior_auth(features, context=None):
    context = context or {}

    pa_required, pa_prob, approval_prob = run_pa_model(features)

    recommended_path = (
        "fast" if pa_required and approval_prob > 0.65 else "standard"
    )

    estimated_hours = 2 if recommended_path == "fast" else 24

    # ---- MLflow is optional telemetry ----
    try:
        setup_mlflow()
        with mlflow.start_run(run_name="prior_auth_assess"):
            mlflow.log_param("model_version", MODEL_VERSION)
            mlflow.log_param("model_name", MODEL_NAME)
            mlflow.log_param("feature_version", FEATURE_VERSION)
            mlflow.set_tag("model_type", "rules")

            for k, v in context.items():
                mlflow.log_param(k, v)

            mlflow.log_metric("pa_probability", pa_prob)
            mlflow.log_metric("approval_probability", approval_prob)
            mlflow.set_tag("recommended_path", recommended_path)

    except Exception as e:
        logger.warning(f"[MLflow] logging skipped: {e}")

    logger.info("PriorAuthModel set up")
    return {
        "pa_required": pa_required,
        "approval_probability": round(approval_prob, 3),
        "recommended_path": recommended_path,
        "confidence": round(abs(approval_prob - 0.5) + 0.5, 3),
        "model_name": MODEL_NAME,
        "model_version": MODEL_VERSION,
        "feature_version": FEATURE_VERSION,
        "fast_track": recommended_path == "fast",
        "expected_hours": estimated_hours,
    }

def run_pa_model(features: list[float]) -> tuple[bool, float, float]:
    """
    Predicts:
    - whether prior auth is required
    - probability PA is required
    - probability PA will be approved if submitted

    Returns:
        (pa_required, pa_probability, approval_probability)
    """

    if not isinstance(features, list):
        raise ValueError("features must be a list")

    if len(features) < 8:
        raise ValueError("PA feature vector too short")

    # -----------------------------
    # 1. PA REQUIRED PROBABILITY
    # -----------------------------
    # Example feature usage (you can tune these later):
    # [0] terminal illness
    # [1] chronic condition count
    # [2] controlled substance
    # [3] refill count
    # [4] days supply
    # [5] age
    # [6] days since last refill
    # [7] chronic flag

    risk_score = (
            0.30 * features[2] +              # controlled substance
            0.25 * features[4] / 90 +          # long days supply
            0.20 * features[6] / 180 +         # refill gap
            0.15 * features[1] +               # comorbidities
            0.10 * (features[5] / 100)         # age
    )

    pa_probability = 1 / (1 + math.exp(-risk_score))
    pa_required = pa_probability >= PA_REQUIRED_THRESHOLD

    # -----------------------------
    # 2. APPROVAL PROBABILITY
    # -----------------------------
    if not pa_required:
        approval_probability = 1.0
    else:
        approval_score = (
                0.35 * (1 - features[2]) +     # non-controlled meds approve easier
                0.30 * features[0] +           # terminal illness priority
                0.20 * features[7] +           # chronic condition justification
                0.15 * (1 - features[6] / 365) # refill compliance
        )

        # add small stochastic noise to avoid hard edges
        approval_probability = max(
            0.05,
            min(0.95, approval_score + random.uniform(-0.05, 0.05))
        )

    return (
        bool(pa_required),
        round(pa_probability, 3),
        round(approval_probability, 3),
    )