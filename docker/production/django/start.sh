#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py migrate --no-input
python manage.py collectstatic --no-input

# Check for environment variable SERVICE_TYPE if not create empty
SERVICE_TYPE=${SERVICE_TYPE:-""}

# Kubernetes will pass the SERVICE_TYPE environment variable
if [ "$SERVICE_TYPE" = "web" ]; then
    # Run with gunicorn for wsgi - APIs
    gunicorn light_messages.wsgi:application \
        --bind 0.0.0.0:8000 \
        --workers 1 \
        --reload \
        --access-logfile - \
        --error-logfile -
elif [ "$SERVICE_TYPE" = "channel" ]; then
    # Run with daphne for asgi - WebSocket
    daphne light_messages.asgi:application \
        --bind 0.0.0.0 \
        --port 8000
else
    echo "Run Both Web and Channel (Development | Docker Compose)"
    python manage.py runserver 0.0.0.0:8000
fi