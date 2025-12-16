import time
import random

class MockPharmacyClient:
    def __init__(self, pharmacy):
        self.pharmacy = pharmacy

    def submit_refill(self, refill_id, patient, prescription):
        # Simulate processing time
        time.sleep(1)
        # Simulate success or failure
        success = random.choice([True, True, True, False])
        if success:
            return {
                "success": True,
                "message": f"Refill {refill_id} accepted by {self.pharmacy.name}. ETA ~45 minutes"
            }
        else:
            return {
                "success": False,
                "message": f"Refill {refill_id} failed at {self.pharmacy.name}: out of stock"
            }
