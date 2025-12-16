from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from main.db.session import get_db, SessionLocal
from main.db import models
from main.services.agent import run_agent_on_refill
from datetime import datetime
import uuid

router = APIRouter()

class RefillCreate(BaseModel):
    patient_id: str
    prescription_id: str
    icd_codes: list = []

@router.post("/refills")
async def create_refill(payload: RefillCreate, background_tasks: BackgroundTasks):
    db = SessionLocal()
    # minimal validation
    patient = db.query(models.Patient).filter(models.Patient.id == payload.patient_id).first()
    presc = db.query(models.Prescription).filter(models.Prescription.id == payload.prescription_id).first()
    if not patient or not presc:
        db.close()
        raise HTTPException(status_code=400, detail="Patient or Prescription not found (demo: create sample data first).")
    refill = models.RefillRequest(
        id=str(uuid.uuid4()),
        patient_id=payload.patient_id,
        prescription_id=payload.prescription_id,
        status='queued',
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(refill)
    db.commit()
    db.refresh(refill)
    db.close()
    background_tasks.add_task(run_agent_on_refill, refill.id)
    return {"refill_id": refill.id, "status": "queued"}

@router.get("/refills/{refill_id}")
def get_refill(refill_id: str):
    db = SessionLocal()
    refill = db.query(models.RefillRequest).filter(models.RefillRequest.id == refill_id).first()
    db.close()
    if not refill:
        raise HTTPException(status_code=404, detail="Not found")
    return {
        "id": refill.id,
        "status": refill.status,
        "severity_score": refill.severity_score,
        "routed_pharmacy_id": refill.routed_pharmacy_id,
        "api_response": refill.api_response
    }
