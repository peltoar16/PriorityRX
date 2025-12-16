from fastapi import FastAPI
from main.routers import refills, patients, pharmacies
from main.db import init_db

app = FastAPI(title="PriorityRx Demo Agent")

# Initialize DB (sqlite demo)
@app.on_event("startup")
async def startup():
    init_db()

app.include_router(refills.router)
app.include_router(patients.router)
app.include_router(pharmacies.router)