from fastapi import FastAPI
from app.api import jobs
from app.celery_app import celery
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(title="PriorityRx Agent Service")

app.include_router(jobs.router)

@app.get('/health')
def health():
    return {'status': 'ok'}
