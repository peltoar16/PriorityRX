#!/bin/bash
# Run uvicorn and a celery worker in separate terminals if desired.
echo "Start FastAPI:"
echo "uvicorn app.main:app --reload --port 9000"
echo "Start Celery worker:"
echo "celery -A app.celery_app.celery worker --loglevel=info"
