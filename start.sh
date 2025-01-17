#!/bin/bash
export PORT="${PORT:-8000}"
echo "Starting application on port: $PORT"
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Environment variables:"
env

exec gunicorn --bind "0.0.0.0:$PORT" \
    --workers 4 \
    --timeout 120 \
    --log-level debug \
    --error-logfile - \
    --access-logfile - \
    --capture-output \
    app:app 