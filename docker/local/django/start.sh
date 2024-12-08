#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py migrate --no-input
python manage.py collectstatic --no-input

# Fix: Update daphne command to use correct ASGI application path
daphne -b 0.0.0.0 -p 8000 light_messages.asgi:application