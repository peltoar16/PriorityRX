from typing import Optional, List

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, Field, EmailStr
from main.db.session import get_db, SessionLocal
from main.db import models
from main.services.agent import run_agent_on_refill
from datetime import datetime, date
import uuid

router = APIRouter()

class PatientInfo(BaseModel):
    external_patient_id: str = Field(..., description="Provider's patient identifier")
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    terminal_illness: bool = False
    icd10_primary_code: Optional[str] = None
    icd10_additional_codes: List[str] = []

class PrescriptionInfo(BaseModel):
    external_prescription_id: str = Field(..., description="Provider prescription identifier")
    medication_name: str
    dosage: Optional[str] = None
    quantity: Optional[int] = None
    days_supply: Optional[int] = None
    refills_remaining: Optional[int] = None
    is_controlled: bool = False

class RefillCreate(BaseModel):
    request_source: str = Field(..., example="walgreens_api")
    patient: PatientInfo
    prescription: PrescriptionInfo
    requested_at: Optional[str] = None

@router.post("/refills")
async def create_refill(payload: RefillCreate, background_tasks: BackgroundTasks):
    db = SessionLocal()
    # minimal validation
    # -----------------------
    # 1. Find or create patient
    # -----------------------
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.external_id == payload.patient.external_patient_id)
        .first()
    )

    if not patient:
        patient = models.Patient(
            id=str(uuid.uuid4()),
            external_id=payload.patient.external_patient_id,
            first_name=payload.patient.first_name,
            last_name=payload.patient.last_name,
            phone=payload.patient.phone,
            email=payload.patient.email,
            terminal_illness=payload.patient.terminal_illness,
            icd10_primary_code=payload.patient.icd10_primary_code,
            icd10_additional_codes=",".join(payload.patient.icd10_additional_codes),
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)

    # -----------------------
    # 2. Find or create prescription
    # -----------------------
    prescription = (
        db.query(models.Prescription)
        .filter(models.Prescription.external_id == payload.prescription.external_prescription_id)
        .first()
    )

    if not prescription:
        prescription = models.Prescription(
            id=str(uuid.uuid4()),
            external_id=payload.prescription.external_prescription_id,
            medication_name=payload.prescription.medication_name,
            dosage=payload.prescription.dosage,
            quantity=payload.prescription.quantity,
            days_supply=payload.prescription.days_supply,
            is_controlled=payload.prescription.is_controlled
        )
        db.add(prescription)
        db.commit()
        db.refresh(prescription)

    # -----------------------
    # 3. Create refill request
    # -----------------------
    refill = models.RefillRequest(
        id=str(uuid.uuid4()),
        patient_id=patient.id,
        prescription_id=prescription.id,
        status="queued",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(refill)
    db.commit()
    db.refresh(refill)

    # -----------------------
    # 4. Trigger agent pipeline
    # -----------------------
    background_tasks.add_task(run_agent_on_refill, refill.id)

    patient_priority = patient.priority_level

    db.close()

    return {
        "refill_id": refill.id,
        "status": "queued",
        "patient_priority": patient_priority,
    }

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
