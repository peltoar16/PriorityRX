import mlflow
import os

_mlflow_ready = False

def setup_mlflow():
    global _mlflow_ready
    if _mlflow_ready:
        return

    mlflow.set_tracking_uri(
        os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    )

    # DO NOT fail app startup if MLflow is down
    try:
        mlflow.set_experiment("priorityrx-agent")
        _mlflow_ready = True
    except Exception as e:
        print(f"[MLflow] WARNING: MLflow not ready: {e}")