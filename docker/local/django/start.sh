#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

python manage.py migrate --no-input
python manage.py collectstatic --no-input

### Run daphne server
## daphne -b 0.0.0.0 -p 8000 light_messages.asgi:application

### Run with runserver
python manage.py runserver 0.0.0.0:8000