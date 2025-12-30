import asyncio
from typing import List
from app.pharmacies.base import PharmacyAdapter

async def query_pharmacies(
        adapters: List[PharmacyAdapter],
        *,
        ndc: str,
        zip_code: str,
        quantity: int,
):
    tasks = [
        adapter.check_availability(
            ndc=ndc,
            zip_code=zip_code,
            quantity=quantity,
        )
        for adapter in adapters
    ]

    return await asyncio.gather(*tasks)