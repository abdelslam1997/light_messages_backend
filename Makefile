DOCKER_COMPOSE = docker compose -f local_docker_compose.yml
SERVICE = light_messages_backend
path = .

build:
	$(DOCKER_COMPOSE) build

build-no-cache:
	$(DOCKER_COMPOSE) build --no-cache

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

logs:
	$(DOCKER_COMPOSE) logs -f

terminal:
	$(DOCKER_COMPOSE) exec $(SERVICE) bash

create-superuser:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) python manage.py createsuperuser

makemigrations:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) python manage.py makemigrations

migrate:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) python manage.py migrate

pytest:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) pytest -p no:warnings --cov=. -v $(path)

pytest-print:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) pytest -s -p no:warnings --cov=. -v $(path)

pytest-html:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) pytest -p no:warnings --cov=. --cov-report html $(path)

# Example usage:
# make pytest path=tests/test_file.py
# make pytest-print path=tests/test_file.py
# make pytest-html path=tests/test_file.py
