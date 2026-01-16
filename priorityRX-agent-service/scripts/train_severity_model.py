import mlflow
import mlflow.sklearn
import joblib
from pathlib import Path

from app.mlflow_client import setup_mlflow
from app.models.severity_model import train_dummy_model

MODEL_NAME = "SeverityScoringModel"
ARTIFACT_DIR = Path("artifacts")
MODEL_FILE = ARTIFACT_DIR / "severity_model.joblib"


def main():
    setup_mlflow()

    model = train_dummy_model()

    ARTIFACT_DIR.mkdir(exist_ok=True)
    joblib.dump(model, MODEL_FILE)

    with mlflow.start_run(run_name="severity_model_training"):
        mlflow.log_param("model_type", type(model).__name__)
        mlflow.log_param("feature_count", 8)

        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="model",
            registered_model_name=MODEL_NAME,
        )

        mlflow.log_artifact(str(MODEL_FILE))


if __name__ == "__main__":
    main()