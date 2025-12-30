import mlflow

def log_pharmacy_signals(signals: list[dict]):
    for s in signals:
        mlflow.log_metric(
            f"{s['pharmacy']}_available",
            float(s["available"]),
        )
        mlflow.log_metric(
            f"{s['pharmacy']}_wait_hours",
            s["estimated_wait_hours"],
        )