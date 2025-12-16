import time
from app.celery_app import celery
from app.model_loader import ModelManager
from app.db.client import DBClient

@celery.task(bind=True)
def enqueue_refill_job(self, refill_id: str):
    # simple worker flow: load model, compute mock features, infer, choose pharmacy mock, update db, notify
    model_mgr = ModelManager()
    model = model_mgr.get_model()  # returns a predictor object
    # mock features
    features = model_mgr.build_demo_features(refill_id)
    pred = model_mgr.predict(model, features)
    # mock decision
    chosen = 'walgreens_demo' if pred.get('eta', 999) < 60 else 'cvs_demo'
    # persist decision to DB (demo)
    DBClient.log_routing_decision(refill_id, chosen, pred)
    # simulate calling pharmacy API
    time.sleep(1)
    # simulate webhook outcome
    DBClient.log_outcome(refill_id, chosen, success=True, time_to_fulfill_minutes=45)
    return {'refill_id': refill_id, 'chosen': chosen, 'pred': pred}
