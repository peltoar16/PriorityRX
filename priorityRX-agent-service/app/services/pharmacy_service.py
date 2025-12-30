from typing import List

from app.features.patient_features import PatientLocation
from app.pharmacies.mock import MockPharmacyAdapter
from app.pharmacies.registry import query_pharmacies
from app.features.pharmacy_features import build_ranking_matrix, haversine_km
from app.observability.myflow_logging import log_pharmacy_signals
from sqlalchemy.orm import Session
from app.db.models.pharmacies import PharmacyORM
from app.domain.pharmacies import Pharmacy

import os

USE_MOCKS = os.getenv("USE_MOCK_PHARMACIES", "true") == "true"
MAX_DISTANCE_KM = 25  # configurable

def get_adapters():
    if USE_MOCKS:
        return [
            MockPharmacyAdapter("CVS"),
            MockPharmacyAdapter("Walgreens"),
            MockPharmacyAdapter("Independent"),
        ]

    # later:
    # return [CVSAdapter(...), WalgreensAdapter(...)]
    raise NotImplementedError


async def fetch_pharmacy_features(*, ndc: str, zip_code: str, quantity: int):
    adapters = get_adapters()

    signals = await query_pharmacies(
        adapters,
        ndc=ndc,
        zip_code=zip_code,
        quantity=quantity,
    )

    log_pharmacy_signals(signals)

    ranking_features = build_ranking_matrix(signals)

    return signals, ranking_features

def get_candidate_pharmacies(
        db: Session,
        patient_location: PatientLocation,
        limit: int = 10,
) -> List[Pharmacy]:

    query = db.query(PharmacyORM)

    # Delivery / pickup preference filtering
    if patient_location.prefers_delivery:
        query = query.filter(PharmacyORM.supports_delivery.is_(True))
    else:
        query = query.filter(PharmacyORM.supports_pickup.is_(True))

    pharmacies = query.all()

    candidates: list[Pharmacy] = []

    for ph in pharmacies:
        distance = haversine_km(
            patient_location.latitude,
            patient_location.longitude,
            ph.latitude,
            ph.longitude,
        )

        if distance > MAX_DISTANCE_KM:
            continue

        candidates.append(
            Pharmacy(
                id=ph.id,
                name=ph.name,
                distance_km=distance,
                avg_response_minutes=ph.avg_response_minutes or 60,
                fill_success_rate=ph.fill_success_rate or 0.85,
                stock_probability=ph.stock_probability or 0.75,
                api_enabled=ph.api_enabled,
                supports_controlled=ph.supports_controlled,
                supports_delivery=ph.supports_delivery,
                supports_pickup=ph.supports_pickup,
            )
        )

    # Sort by proximity first (strong patient convenience bias)
    candidates.sort(key=lambda p: p.distance_km)

    return candidates[:limit]

def rank_pharmacies(pharmacies, severity_score: float):
    """
    Returns pharmacies sorted best → worst
    """

    def score(pharmacy):
        # weights change based on severity
        if severity_score >= 0.85:
            w_distance = 0.2
            w_response = 0.4
            w_stock = 0.4
        else:
            w_distance = 0.5
            w_response = 0.25
            w_stock = 0.25

        return (
                -w_distance * pharmacy.distance_km
                -w_response * pharmacy.avg_response_minutes
                +w_stock * pharmacy.stock_probability
        )

    return sorted(pharmacies, key=score, reverse=True)