#!/bin/bash

# Set default port if not provided
if [ -z "$PORT" ]; then
    export PORT=8000
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Start the application with gunicorn
echo "Starting application on port $PORT..."
exec gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload 