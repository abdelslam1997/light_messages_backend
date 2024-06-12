build:
	docker compose -f local_docker_compose.yml build

up:
	docker compose -f local_docker_compose.yml up -d

down:
	docker compose -f local_docker_compose.yml down

terminal:
	docker compose -f local_docker_compose.yml exec light_messages_backend bash

makemigrations:
	docker compose -f local_docker_compose.yml run --rm light_messages_backend python manage.py makemigrations

migrate:
	docker compose -f local_docker_compose.yml run --rm light_messages_backend python manage.py migrate

pytest:
	docker compose -f local_docker_compose.yml run --rm light_messages_backend pytest -p no:warnings --cov=. -v

pytest-print:
	docker compose -f local_docker_compose.yml run --rm light_messages_backend pytest -s -p no:warnings --cov=. -v

pytest-html:
	docker compose -f local_docker_compose.yml run --rm light_messages_backend pytest -p no:warnings --cov=. --cov-report html