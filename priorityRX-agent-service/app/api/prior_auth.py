import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, conlist, Field
from typing import Dict, Optional, Annotated, List

from app.services.prior_auth_service import assess_prior_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prior-auth", tags=["Prior Auth"])

Features8 = Annotated[
    List[float],
    Field(min_length=8, max_length=8)
]

class PriorAuthAssessRequest(BaseModel):
    features: Features8
    context: Optional[dict] = None


class PriorAuthAssessResponse(BaseModel):
    pa_required: bool
    approval_probability: float
    recommended_path: str
    confidence: float
    model_name: str
    model_version: str
    feature_version: str
    fast_track: bool
    expected_hours: float


@router.post(
    "/assess",
    response_model=PriorAuthAssessResponse,
)
def assess_prior_auth_endpoint(req: PriorAuthAssessRequest):

    try:
        return assess_prior_auth(
            features=req.features,
            context=req.context,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception("Prior auth assessment failed")
        raise HTTPException(status_code=500, detail=str(e))