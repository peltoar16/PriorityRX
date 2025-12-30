import math

def build_feature_vector(pharmacy_signal: dict) -> list[float]:
    return [
        float(pharmacy_signal["available"]),
        pharmacy_signal["estimated_wait_hours"],
        pharmacy_signal["distance_miles"],
        pharmacy_signal["confidence"],
    ]


def build_ranking_matrix(signals: list[dict]):
    return [build_feature_vector(signal) for signal in signals]

def normalize(value, min_v, max_v):
    return max(0.0, min(1.0, (value - min_v) / (max_v - min_v)))


def pharmacy_score(pharmacy, severity_score):
    # Severity-aware weights
    if severity_score >= 0.85:  # critical
        weights = {
            "response": 0.35,
            "distance": 0.15,
            "stock": 0.30,
            "success": 0.15,
            "api": 0.05,
        }
    else:
        weights = {
            "response": 0.25,
            "distance": 0.30,
            "stock": 0.20,
            "success": 0.20,
            "api": 0.05,
        }

    response_score = 1 - normalize(pharmacy.avg_response_minutes, 5, 120)
    distance_score = 1 - normalize(pharmacy.distance_km, 0, 50)
    stock_score = pharmacy.stock_probability
    success_score = pharmacy.fill_success_rate
    api_score = 1.0 if pharmacy.api_enabled else 0.0

    return (
            weights["response"] * response_score +
            weights["distance"] * distance_score +
            weights["stock"] * stock_score +
            weights["success"] * success_score +
            weights["api"] * api_score
    )

def haversine_km(lat1, lon1, lat2, lon2) -> float:
    R = 6371  # Earth radius (km)

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    )

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))