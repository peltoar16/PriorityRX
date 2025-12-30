import httpx
from app.pharmacies.base import PharmacyAdapter

class CVSAdapter(PharmacyAdapter):
    name = "CVS"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def check_availability(self, *, ndc, zip_code, quantity):
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                "https://api.cvs.com/pharmacy/availability",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "ndc": ndc,
                    "zip": zip_code,
                    "quantity": quantity,
                },
            )

        if resp.status_code != 200:
            return self._fallback(ndc, zip_code)

        data = resp.json()

        return {
            "pharmacy": self.name,
            "available": data["in_stock"],
            "estimated_wait_hours": data.get("wait_hours", 48),
            "distance_miles": data.get("distance", 5),
            "confidence": 0.9,
        }

    def _fallback(self, ndc, zip_code):
        return {
            "pharmacy": self.name,
            "available": False,
            "estimated_wait_hours": 72,
            "distance_miles": 10,
            "confidence": 0.3,
        }