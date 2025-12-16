#!/bin/bash
echo "Starting docker-compose services..."
docker-compose up -d
echo "Done. Redis on 6379, MinIO on 9000, MLflow on 5000"
