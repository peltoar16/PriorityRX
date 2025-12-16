import time
from main.db.session import SessionLocal
from main.db import models
from main.services.scoring import compute_severity
from main.services.routing import pick_best_pharmacy
from main.services.notifications import notify_patient
import uuid
from datetime import datetime

def run_agent_on_refill(refill_id: str):
    db = SessionLocal()
    refill = db.query(models.RefillRequest).filter(models.RefillRequest.id == refill_id).first()
    if not refill:
        db.close()
        return
    patient = db.query(models.Patient).filter(models.Patient.id == refill.patient_id).first()
    presc = db.query(models.Prescription).filter(models.Prescription.id == refill.prescription_id).first()
    # For demo: collect icd codes from patient.icd10_additional_codes
    icd_codes = (patient.icd10_additional_codes or "").split(",") if patient.icd10_additional_codes else []
    # Step 1: compute severity
    score = compute_severity(patient, presc, icd_codes)
    refill.severity_score = score
    db.commit()
    # Step 2: pick pharmacy
    pharmacy = pick_best_pharmacy(presc, score)
    if pharmacy:
        refill.routed_pharmacy_id = pharmacy.id
        # Step 3: place order via mock integration
        from main.services.pharmacy_integrations.mock_pharmacy import MockPharmacyClient
        client = MockPharmacyClient(pharmacy)
        response = client.submit_refill(refill_id, patient, presc)
        refill.api_response = response.get('message')
        refill.status = 'routed' if response.get('success') else 'error'
        db.commit()
        # Step 4: notify
        notify_patient(patient, f"Your refill has been routed to {pharmacy.name}. Status: {refill.status}")
    else:
        refill.status = 'no_pharmacy_found'
        db.commit()
        notify_patient(patient, "We couldn't find a pharmacy to fulfill your refill at this time.")
    db.close()
