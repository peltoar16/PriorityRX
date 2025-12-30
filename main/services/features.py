from datetime import datetime
from typing import List

def build_features(patient, prescription) -> list[float]:
    """
    Feature order MUST match training.
    """

    now = datetime.utcnow()

    age = (
        (now.date() - patient.date_of_birth).days / 365.25
        if patient.date_of_birth else 0.0
    )

    days_since_last_refill = (
        (now - prescription.last_refill_at).days
        if prescription.last_refill_at else 0.0
    )

    chronic_icds = {"E11", "I10", "J45"}  # diabetes, hypertension, asthma
    chronic_flag = int(
        patient.icd10_primary_code in chronic_icds
    )

    return [
        float(patient.terminal_illness),
        float(len((patient.icd10_additional_codes or "").split(","))),
        float(1 if prescription.is_controlled else 0),
        float(prescription.refill_count or 0),
        float(prescription.days_supply or 0),
        float(age),
        float(days_since_last_refill),
        float(chronic_flag),
    ]