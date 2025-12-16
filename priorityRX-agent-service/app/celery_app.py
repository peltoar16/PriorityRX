import os
from celery import Celery
from dotenv import load_dotenv
load_dotenv()

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

celery = Celery('agent_tasks', broker=REDIS_URL, backend=REDIS_URL)
celery.conf.task_routes = {'app.tasks.*': {'queue': 'refill_jobs'}}
