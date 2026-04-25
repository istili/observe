#!/bin/bash
set -euo pipefail

# Script to manually trigger the batch pipeline
# Useful for testing and generating data

echo "🚀 Triggering batch pipeline..."

# Find the scheduler container
SCHEDULER=$(docker ps --filter "name=^airflow-scheduler$" --format '{{.ID}}')

if [ -z "$SCHEDULER" ]; then
    echo "❌ Airflow scheduler not found. Run: docker compose up -d"
    exit 1
fi

# Trigger the DAG
docker exec "$SCHEDULER" airflow dags trigger batch_pipeline

echo "✅ Pipeline triggered! Check Grafana in 30 seconds."