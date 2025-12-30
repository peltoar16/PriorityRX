from app.domain.patient import PatientLocation
from app.db.models.patient import Patient

def get_patient_location(patient: Patient) -> PatientLocation:
    if patient.latitude is None or patient.longitude is None:
        raise ValueError("Patient location missing")

    return PatientLocation(
        latitude=patient.latitude,
        longitude=patient.longitude,
        prefers_delivery=patient.prefers_delivery,
    )