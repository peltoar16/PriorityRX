import os
import joblib
import numpy as np
from typing import Dict
from sklearn.ensemble import GradientBoostingRegressor

MODEL_PATH = os.getenv('MODEL_PATH', 'models/demo_eta_model.joblib')

class ModelManager:
    def __init__(self):
        # lazy load
        self._model = None

    def get_model(self):
        if self._model is None:
            self._model = self._load_model()
        return self._model

    def _load_model(self):
        # In demo, create a simple model if not exists
        if not os.path.exists(MODEL_PATH):
            # train a dummy model
            from sklearn.datasets import make_regression
            X, y = make_regression(n_samples=100, n_features=5, noise=0.1, random_state=42)
            model = GradientBoostingRegressor()
            model.fit(X, y)
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            joblib.dump(model, MODEL_PATH)
            return model
        return joblib.load(MODEL_PATH)

    def predict(self, model, features: Dict):
        # expects features dict; convert to vector for demo
        vec = np.array([features.get('f'+str(i), 0.0) for i in range(5)]).reshape(1, -1)
        eta_pred = float(model.predict(vec)[0])
        # map to a simple positive eta
        eta = max(5, int(abs(eta_pred)))
        return {'eta': eta}

    def build_demo_features(self, refill_id: str):
        # produce deterministic features for demo
        h = sum(ord(c) for c in refill_id)
        return {f'f{i}': (h % (i+7)) / 10.0 for i in range(5)}
