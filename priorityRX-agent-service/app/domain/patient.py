from dataclasses import dataclass
from typing import Optional


@dataclass
class PatientLocation:
    latitude: float
    longitude: float
    prefers_delivery: bool
