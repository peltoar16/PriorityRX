import time

import requests

from main.db.session import SessionLocal
from main.db import models
from main.services.features import build_features
from main.services.scoring import compute_severity
from main.services.routing import pick_best_pharmacy
from main.services.notifications import notify_patient
import uuid
from datetime import datetime, timedelta

AGENT_BASE_URL = "http://127.0.01:9000"
PRIORITY_TTL = timedelta(hours=24)
MAX_FEATURES = 8;

def run_agent_on_refill(refill_id: str):
    db = SessionLocal()

    refill = db.query(models.RefillRequest).get(refill_id)
    patient = db.query(models.Patient).get(refill.patient_id)
    prescription = db.query(models.Prescription).get(refill.prescription_id)

    if not refill or not patient or not prescription:
        db.close()
        return

    now = datetime.utcnow()

    needs_scoring = (
            patient.severity_score is None
            or patient.last_scored_at is None
            or now - patient.last_scored_at > PRIORITY_TTL
    )

    # ------------------------------
    # CALL AGENT SERVICE /process
    # ------------------------------
    if needs_scoring:
        features = build_features(patient, prescription)
        if len(features) != MAX_FEATURES:
            raise RuntimeError(f"Feature mismatch: {features}")

        resp = requests.post(
            f"{AGENT_BASE_URL}/process",
            json={
                "patient_id": patient.id,
                "features": features,
            },
            timeout=5,
        )

        data = resp.json()

        patient.severity_score = data["severity_score"]
        patient.priority_level = data["queue"]
        patient.last_scored_at = now

        db.commit()

    # ---- Feature Engineering (simple demo) ----
    features = build_features(patient, prescription)


    # ---- 1. Inference ----
    score_resp = requests.post(
        f"{AGENT_BASE_URL}/score",
        json={"features": features},
        timeout=5,
    )

    severity_score = score_resp.json()["severity_score"]

    # ---- 2. Routing ----
    if severity_score > 0.8 and patient.priority_level == 'critical':
        pharmacy = (
            db.query(models.Pharmacy)
            .filter(models.Pharmacy.api_enabled == True)
            .first()
        )
    else:
        pharmacy = db.query(models.Pharmacy).first()

    refill.routed_pharmacy_id = pharmacy.id if pharmacy else None
    refill.updated_at = datetime.utcnow()
    refill.severity_score = patient.severity_score
    refill.status = "routed"

    db.commit()

    # ---- 3. Async learning ----
    requests.post(
        f"{AGENT_BASE_URL}/jobs",
        json={"refill_id": refill.id},
        timeout=2,
    )

    db.close()