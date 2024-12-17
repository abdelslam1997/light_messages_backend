DOCKER_COMPOSE = docker compose -f local_docker_compose.yml
SERVICE = light_messages_backend
path = .

rebuild:
	$(DOCKER_COMPOSE) down
	$(DOCKER_COMPOSE) build
	$(DOCKER_COMPOSE) up -d
	$(DOCKER_COMPOSE) logs -f

build:
	$(DOCKER_COMPOSE) build

build-no-cache:
	$(DOCKER_COMPOSE) build --no-cache

remove-all:
	echo "Stopping and removing all containers, networks, and volumes..."
	$(DOCKER_COMPOSE) down --volumes --remove-orphans
	
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

redis-cli:
	$(DOCKER_COMPOSE) exec redis redis-cli

pytest:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) pytest -rP -p no:warnings --cov=. -v $(path)

pytest-print:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) pytest -s -p no:warnings --cov=. -v $(path)

pytest-html:
	$(DOCKER_COMPOSE) run --rm $(SERVICE) pytest -p no:warnings --cov=. --cov-report html $(path)

minikube-tunnel:
	minikube tunnel

minikube-restart:
	minikube stop
	minikube start
	minikube addons enable ingress
	kubectl apply -k k8s/overlays/local

k8s-reset:
	kubectl delete -f k8s/overlays/local/
	kubectl apply -k k8s/overlays/local
	@echo "Wait for ingress to be ready..."
	sleep 10
	minikube tunnel

kubectl-apply:
	kubectl apply -k k8s/overlays/local/

kubectl-delete:
	kubectl delete -f k8s/overlays/local/

kubectl-delete-all:
	kubectl delete ingress --all
	kubectl delete services --all
	kubectl delete deployments --all
	kubectl delete pods --all

k8s-restart:
	kubectl delete ingress --all
	kubectl delete services --all
	kubectl delete deployments --all
	kubectl delete pods --all
	kubectl apply -k k8s/overlays/local
	kubectl get all

### Example usage:
# make pytest 
# make pytest path=tests/test_file.py
# make pytest-print path=tests/test_file.py
# make pytest-html path=tests/test_file.py
