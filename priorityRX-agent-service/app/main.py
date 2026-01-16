from fastapi import FastAPI

from app.api import jobs, patient_processing, scoring, prior_auth
from dotenv import load_dotenv
import app.celery_app
import app.tasks

load_dotenv()

app = FastAPI(title="PriorityRx Agent Service")
app.include_router(jobs.router)
app.include_router(patient_processing.router)
app.include_router(scoring.router)
app.include_router(prior_auth.router)

