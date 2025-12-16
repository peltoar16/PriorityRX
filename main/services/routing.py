from main.db.session import SessionLocal
from main.db import models
import math

def get_available_pharmacies_for_med(medication_id):
    db = SessionLocal()
    # naive: return all pharmacies with api_enabled True first, otherwise all
    items = db.query(models.Pharmacy).all()
    db.close()
    return items

def pick_best_pharmacy(prescription, severity_score):
    pharmacies = get_available_pharmacies_for_med(prescription.medication_id)
    if not pharmacies:
        return None
    # demo ranking: prefer api_enabled pharmacies, then random stable selection
    pharmacies_sorted = sorted(pharmacies, key=lambda p: (0 if p.api_enabled else 1, p.name))
    return pharmacies_sorted[0]
