import random
from app.pharmacies.base import PharmacyAdapter

class MockPharmacyAdapter(PharmacyAdapter):
    def __init__(self, name: str):
        self.name = name

    async def check_availability(self, *, ndc, zip_code, quantity):
        seed = hash(f"{self.name}-{ndc}-{zip_code}")
        random.seed(seed)

        available = random.random() > 0.3

        return {
            "pharmacy": self.name,
            "available": available,
            "estimated_wait_hours": random.choice([0, 12, 24, 48]),
            "distance_miles": random.uniform(1, 12),
            "confidence": 0.6,
        }