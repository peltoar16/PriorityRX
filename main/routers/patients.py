from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from main.db.session import SessionLocal
from main.db import models
import uuid
from datetime import datetime

router = APIRouter()

class PatientCreate(BaseModel):
    id: str = None
    first_name: str
    last_name: str
    phone: str = None
    email: str = None
    terminal_illness: bool = False
    icd10_primary_code: str = None
    icd10_additional_codes: list = []

@router.post("/patients")
def create_patient(data: PatientCreate):
    db = SessionLocal()
    pid = data.id or str(uuid.uuid4())
    patient = models.Patient(
        id=pid,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone,
        email=data.email,
        terminal_illness=data.terminal_illness,
        icd10_primary_code=data.icd10_primary_code,
        icd10_additional_codes=",".join(data.icd10_additional_codes) if data.icd10_additional_codes else None
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    db.close()
    return {"patient_id": patient.id}

@router.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    db = SessionLocal()
    p = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    db.close()
    if not p:
        raise HTTPException(status_code=404, detail="not found")
    return {
        "id": p.id,
        "first_name": p.first_name,
        "last_name": p.last_name,
        "phone": p.phone,
        "email": p.email,
        "terminal_illness": p.terminal_illness
    }
