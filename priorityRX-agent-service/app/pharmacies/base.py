from abc import ABC, abstractmethod
from typing import Dict

class PharmacyAdapter(ABC):
    name: str

    @abstractmethod
    async def check_availability(
            self,
            *,
            ndc: str,
            zip_code: str,
            quantity: int
    ) -> Dict:
        """
        Returns structured availability signals
        """
        pass
