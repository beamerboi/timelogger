#!/bin/bash
export PORT="${PORT:-8000}"
exec gunicorn --bind "0.0.0.0:$PORT" --workers 4 --timeout 120 app:app 