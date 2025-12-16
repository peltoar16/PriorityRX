from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from main.db.session import SessionLocal
from main.db import models
import uuid

router = APIRouter()

class PharmacyCreate(BaseModel):
    id: str = None
    name: str
    type: str = "retail"
    api_enabled: bool = False

@router.post("/pharmacies")
def create_pharmacy(data: PharmacyCreate):
    db = SessionLocal()
    pid = data.id or str(uuid.uuid4())
    ph = models.Pharmacy(
        id=pid,
        name=data.name,
        type=data.type,
        api_enabled=data.api_enabled
    )
    db.add(ph)
    db.commit()
    db.refresh(ph)
    db.close()
    return {"pharmacy_id": ph.id}

@router.get("/pharmacies")
def list_pharmacies():
    db = SessionLocal()
    items = db.query(models.Pharmacy).all()
    db.close()
    return [{"id": p.id, "name": p.name, "type": p.type, "api_enabled": p.api_enabled} for p in items]
