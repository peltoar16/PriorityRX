from dataclasses import dataclass
from typing import Optional


@dataclass
class Pharmacy:
    # Identity
    id: str
    name: str
    # Location
    distance_km: float
    # Operational metrics (rolling averages)
    avg_response_minutes: float
    fill_success_rate: float  # 0.0 - 1.0
    # Inventory
    stock_probability: float  # 0.0 - 1.0
    # Capabilities
    api_enabled: bool
    supports_controlled: bool
    # Patient decision to obtaining prescription
    supports_delivery: bool
    supports_pickup: bool
    # Learning / audit
    last_updated_at: Optional[str] = None