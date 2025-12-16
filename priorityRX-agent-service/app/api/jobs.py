from fastapi import APIRouter
from pydantic import BaseModel
from app.tasks import enqueue_refill_job

router = APIRouter()

class JobRequest(BaseModel):
    refill_id: str

@router.post('/jobs')
async def create_job(req: JobRequest):
    # Enqueue a job to Celery
    task = enqueue_refill_job.delay(req.refill_id)
    return {'task_id': task.id, 'status': 'queued'}
