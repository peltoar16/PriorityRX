import logging

from pydantic import BaseModel
from app.services.severity_service import score_patient, is_terminal
from app.api import jobs
from app.celery_app import celery
from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

router = APIRouter()

class PatientRequest(BaseModel):
    patient_id: str
    features: list[float]

@router.post("/process")
def process(req: PatientRequest):
    try:
        severity_score = score_patient(req.features)

        queue = "critical" if is_terminal(severity_score) else "standard"

        return {
            "severity_score": severity_score,
            "queue": queue,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception("Agent processing failed")
        raise HTTPException(status_code=500, detail=str(e))