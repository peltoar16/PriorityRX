from fastapi import FastAPI

from app.api import jobs, patient_processing, scoring
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PriorityRx Agent Service")
app.include_router(jobs.router)
app.include_router(patient_processing.router)
app.include_router(scoring.router)

