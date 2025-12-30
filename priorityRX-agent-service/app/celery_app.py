import os
from celery import Celery
from kombu import Queue, Exchange
from dotenv import load_dotenv
load_dotenv()

BROKER_URL = os.getenv("CELERY_BROKER_URL")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND")

celery = Celery('priorityrx_agent"', broker=BROKER_URL, backend=BACKEND_URL)
celery.conf.update(
    task_queues=(
        Queue("critical", Exchange("critical"), routing_key="critical"),
        Queue("standard", Exchange("standard"), routing_key="standard"),
    ),
    task_default_queue="standard",
    task_default_exchange="standard",
    task_default_routing_key="standard",
    task_routes={
        "tasks.process_patient": {
            "queue": "standard",
        },
    },
    broker_connection_retry_on_startup=True,
)
celery.conf.task_routes = {'app.tasks.*': {'queue': 'refill_jobs'}}
