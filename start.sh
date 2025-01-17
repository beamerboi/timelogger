#!/bin/bash
export PORT="${PORT:-8000}"
echo "Starting application on port: $PORT"
echo "Current directory: $(pwd)"
echo "Python path: $PYTHONPATH"
echo "Environment variables:"
env

# Run migrations
echo "Running database migrations..."
flask db upgrade || echo "No migrations to run"

# Start the application
exec gunicorn --bind "0.0.0.0:$PORT" \
    --workers 4 \
    --timeout 120 \
    --log-level debug \
    --error-logfile - \
    --access-logfile - \
    --capture-output \
    app:app 