from fastapi import APIRouter
from pydantic import BaseModel
from app.mlflow_client import setup_mlflow
from app.services.severity_service import log_and_register

router = APIRouter()

class SeverityRequest(BaseModel):
    features: list[float]

@router.post("/score")
def score(req: SeverityRequest):
    score = log_and_register(req.features)
    return {"severity_score": score}