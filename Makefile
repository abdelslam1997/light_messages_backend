DOCKER_COMPOSE = docker compose
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


### Kubernetes (Minikube) ###
minikube-tunnel:
	minikube tunnel

minikube-start:
	minikube start
	minikube addons enable ingress
	minikube tunnel

minikube-stop:
	minikube stop

minikube-restart:
	minikube stop
	minikube start
	minikube addons enable ingress
	minikube tunnel

minikube-dashboard:
	minikube dashboard

# Build local image with minikube
minikube-build:
	minikube image build -t light_messages_backend:local -f docker/django/Dockerfile --build-opt build-arg=ENVIRONMENT=local .

## Kubernetes (kubectl) ##
k8s-reapply:
	$(MAKE) k8s-delete
	$(MAKE) k8s-apply

k8s-apply:
	kubectl kustomize --load-restrictor LoadRestrictionsNone k8s/overlays/local | kubectl apply -f -
	kubectl get all

k8s-delete:
	kubectl kustomize --load-restrictor LoadRestrictionsNone k8s/overlays/local | kubectl delete -f -
	kubectl get all

k8s-delete-all:
	kubectl delete all --all

k8s-ingress-controller:
	kubectl get pods -n ingress-nginx

k8s-logs-web:
	kubectl logs -l app=light-messages-web

k8s-logs-channels:
	kubectl logs -l app=light-messages-channels