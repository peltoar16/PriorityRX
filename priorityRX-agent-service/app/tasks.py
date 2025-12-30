import time

from sqlalchemy.orm import session

from app.celery_app import celery
from app.db.models.patient import Patient
from app.features.pharmacy_features import pharmacy_score
from app.services.pharmacy_service import get_candidate_pharmacies
from app.model_loader import ModelManager
from app.db.client import DBClient, SessionLocal
import mlflow

from app.services.patient_service import get_patient_location
from app.services.pharmacy_service import rank_pharmacies
from app.services.severity_service import score_patient

@celery.task(bind=True)
def enqueue_refill_job(self, refill_id: str):
    # simple worker flow: load model, compute mock features, infer, choose pharmacy mock, update db, notify
    model_mgr = ModelManager()
    model = model_mgr.get_model()  # returns a predictor object
    # mock features
    features = model_mgr.build_demo_features(refill_id)
    pred = model_mgr.predict(model, features)
    # mock decision
    chosen = 'walgreens_demo' if pred.get('eta', 999) < 60 else 'cvs_demo'
    # persist decision to DB (demo)
    DBClient.log_routing_decision(refill_id, chosen, pred)
    # simulate calling pharmacy API
    time.sleep(1)
    # simulate webhook outcome
    DBClient.log_outcome(refill_id, chosen, success=True, time_to_fulfill_minutes=45)
    return {'refill_id': refill_id, 'chosen': chosen, 'pred': pred}

@celery.task(bind=True, name="tasks.process_patient", acks_late=True,
             autoretry_for=(Exception,),retry_kwargs={"max_retries": 3, "countdown": 5})
def process_patient(self, patient_id: str, features: list[float]):
    session = SessionLocal()
    try:
        with mlflow.start_run(run_name=f"patient-{patient_id}"):

            # 1. Score patient
            severity_score = score_patient(features)

            mlflow.log_param("patient_id", patient_id)
            mlflow.log_metric("severity_score", severity_score)

            # 2. Load pharmacies (mocked or DB call)
            patient = session.query(Patient).get(patient_id)
            patient_location = get_patient_location(patient)

            pharmacies = get_candidate_pharmacies(
                db=session,
                patient_location=patient_location,
            )

            scored = []
            for p in pharmacies:
                score = pharmacy_score(p, severity_score)

                scored.append({
                    "pharmacy_id": p.id,
                    "score": score,
                    "distance_km": p.distance_km,
                    "response_minutes": p.avg_response_minutes,
                    "stock_probability": p.stock_probability,
                })

                # Per-pharmacy logging
                mlflow.log_metric(f"pharmacy_{p.id}_score", score)

            # Placeholder for pharmacy ranking
            # 3. Rank pharmacies
            ranked = rank_pharmacies(pharmacies, severity_score)

            mlflow.log_metric("pharmacy_count", len(ranked))
            mlflow.log_metric("top_pharmacy_score", ranked[0]["score"])

            return {
                "patient_id": patient_id,
                "severity_score": severity_score,
                "ranked_pharmacies": ranked,
            }
    finally:
        session.close()