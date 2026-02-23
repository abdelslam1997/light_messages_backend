# Light Messages Backend

## Table of Contents

- [Overview](#overview)
  - [Overview Docker Compose (Local Development)](#overview-docker-compose-local-development)
  - [Overview Kubernetes Minikube (Local Deployment)](#overview-kubernetes-minikube-local-deployment)
- [Tech Stack](#tech-stack)
  - [Backend Framework](#backend-framework)
  - [Database & Message Broker](#database--message-broker)
  - [Infrastructure](#infrastructure)
  - [Development Tools](#development-tools)
- [Architecture](#architecture)
  - [Architectural Differences Between Docker and Kubernetes](#architectural-differences-between-docker-and-kubernetes)
    - [Docker Compose](#docker-compose)
    - [Kubernetes](#kubernetes)
- [Project Setup](#project-setup)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
- [Docker Deployment](#docker-deployment)
  - [Docker Deployment Diagram](#docker-deployment-diagram)
  - [Docker Setup Instructions](#docker-setup-instructions)
- [Development](#development)
  - [Running the Project](#running-the-project)
  - [Common Commands](#common-commands)
  - [Accessing Services](#accessing-services)
- [Testing](#testing)
- [API Documentation](#api-documentation)
  - [Authentication](#authentication)
  - [Users](#users)
  - [Messages](#messages)
- [Kubernetes Deployment](#kubernetes-deployment)
  - [Kubernetes Deployment Diagram](#kubernetes-deployment-diagram)
  - [Prerequisites](#prerequisites-1)
  - [Kubernetes Setup Instructions](#kubernetes-setup-instructions)
  - [Deployment Commands](#deployment-commands)
  - [Accessing the Application](#accessing-the-application)
  - [Scaling and Management](#scaling-and-management)


## Overview

This repository features a demo backend showcasing a scalable, real-time messaging API built with **Django**, **Docker**, and **Kubernetes**. 

- **`Frontend Repository:`** [Light Messages Frontend](https://github.com/abdelslam1997)
- **`IaC Repository:`** [Light Messages IaC](https://github.com/abdelslam1997/light_messages_iac) `(Infrastructure as Code to deploy on AWS)`


### Overview Docker Compose (Local Development)
![image](./imgs/docker_compose_architecture.png)

### Overview Kubernetes Minikube (Local Deployment)
![image](./imgs/kubernetes_architecture.png)

## Tech Stack

### Backend Framework
- Django 5.0.x
- Django REST Framework 3.15.x
- Django Channels 4.2.x (WebSocket support)
- Django REST Framework SimpleJWT 5.3.x (JWT authentication)

### Database & Message Broker
- PostgreSQL 15.x
- Redis 7.x (message broker)

### Infrastructure
- Nginx (Layer 7 reverse proxy & load balancing)
- Docker & Docker Compose
- Kubernetes (with minikube)
- Gunicorn (WSGI server)
- Daphne (ASGI server)

### Development Tools
- flake8==7.0.x (linting)
- black==24.4.x (code formatting)
- isort==5.13.x (import sorting)
- pytest==5.0.x (testing)
    - pytest-cov (coverage reporting)
    - pytest-django (Django test integration)
    - pytest-asyncio (async test support)
    - pytest-factoryboy (test factories)
- Faker==0.7.x (fake data generation)

## Architecture

The project architecture consists of the following components:

- **Django Backend**: Serves RESTful API endpoints and handles WebSocket connections for real-time messaging.
- **PostgreSQL Database**: Stores user data and message histories.
- **Redis**: Acts as a message broker for Django Channels, enabling real-time features.
- **Nginx**: Serves as a reverse proxy and static file server.
- **Docker & Docker Compose**: Containerizes the application for consistent development environments.
- **Kubernetes**: Orchestrates container deployment for scalability and high availability.

### Architectural Differences Between Docker and Kubernetes

- **Docker Compose**:
  - Suitable for local development and testing.
  - Uses `docker-compose.yml`, `docker/django/Dockerfile`, and `docker/nginx/nginx.conf.template` for configuration.
  - All services run in a single host environment.
  - Easier setup but limited in scalability.

- **Kubernetes**:
  - Ideal for production-grade deployments.
  - Uses `kustomization.yaml`, `ingress.yaml`, and other manifests for configuration.
  - Supports scaling, self-healing, and load balancing.
  - More complex setup suitable for distributed environments.

## Project Setup

### Prerequisites
- Git [Official Site](https://git-scm.com/)
- Docker & Docker Compose [Official Site](https://docs.docker.com/get-docker/)
- Make (optional) [Official Site](https://www.gnu.org/software/make/)

### Environment Setup
1. Clone the repository:
```bash
git clone https://github.com/abdelslam1997/light_messages_backend.git
cd light_messages_backend
```

2. Create environment files:
```bash
# Create directories
mkdir -p .envs/local

# Create required env files
touch .envs/local/.django.env
touch .envs/local/.postgresql.env
touch .envs/local/.nginx.env
```

3. Configure environment variables:
```bash
# .envs/local/.django.env
SECRET=your_secret_key_here
DJANGO_SETTINGS_MODULE=light_messages.settings.local
DEBUG=true
ALLOWED_HOSTS=localhost,127.0.0.1
ADMIN_URL=admin_123/
CORS_ALLOWED_ORIGINS=http://localhost:5173,
REDIS_HOST=redis
REDIS_PORT=6379

# .envs/local/.postgresql.env
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=light_messages_db
POSTGRES_USER=light_messages_user
POSTGRES_PASSWORD=Pass123456
DATABASE_URL=postgres://light_messages_user:Pass123456@postgres:5432/light_messages_db

# .envs/local/.nginx.env
ADMIN_PATH=admin_123
```

## Docker Deployment

### Docker Deployment Diagram

![Docker Deployment Diagram](./imgs/docker_compose_architecture.png)

### Docker Setup Instructions

The Docker Compose setup is designed for easy local development.

- **Configuration Files**:
  - **`docker-compose.yml`**: Defines services, volumes, and networks.
  - **`docker/django/Dockerfile`**: Specifies how to build the Docker image for the Django application.
  - **`docker/nginx/nginx.conf.template`**: Configures Nginx within the Docker container.

**Steps**:

1. **Build and Start Services**:
   ```bash
   make build
   make up
   ```

  Or without `make`:

  ```bash
  docker compose build
  docker compose up -d
  ```

2. **Apply Migrations and Create Superuser**:
   ```bash
   make migrate
   make create-superuser
   ```

  Or without `make`:

  ```bash
  docker compose run --rm light_messages_backend python manage.py migrate
  docker compose run --rm light_messages_backend python manage.py createsuperuser
  ```

3. **Access Services**:
   - API: http://localhost/api/v1/
   - Admin Interface: http://localhost/admin/
   - WebSocket: ws://localhost/ws/

## Development

### Running the Project

Start all services:
```bash
make up
```

Or without `make`:

```bash
docker compose up -d
```

Make Migrations:
```bash
make makemigrations
```

Or without `make`:

```bash
docker compose run --rm light_messages_backend python manage.py makemigrations
```
Run database migrations:
```bash
make migrate
```

Or without `make`:

```bash
docker compose run --rm light_messages_backend python manage.py migrate
```

Create superuser:
```bash
make create-superuser
```

Or without `make`:

```bash
docker compose run --rm light_messages_backend python manage.py createsuperuser
```

### Common Commands
```bash
# Rebuild all services
make rebuild

# Stop services
make down

# Access backend terminal
make terminal

# Access Redis CLI
make redis-cli
```

Or without `make`:

```bash
# Rebuild all services
docker compose down
docker compose build
docker compose up -d
docker compose logs -f

# Stop services
docker compose down

# Access backend terminal
docker compose exec light_messages_backend bash

# Access Redis CLI
docker compose exec redis redis-cli
```

### Accessing Services
- Backend API: http://localhost/api/v1/
- Admin Interface: http://localhost/admin/
- WebSocket: ws://localhost/ws/

## Testing

Run test suite:
```bash
# Run all tests
make pytest

# Generate HTML report
make pytest-html

# Test specific path
make pytest path=tests/test_file.py
```

Or without `make`:

```bash
# Run all tests
docker compose run --rm light_messages_backend pytest -rP -p no:warnings --cov=. -v

# Generate HTML report
docker compose run --rm light_messages_backend pytest -p no:warnings --cov=. --cov-report html

# Test specific path
docker compose run --rm light_messages_backend pytest -rP -p no:warnings --cov=. -v tests/test_file.py
```

## API Documentation

#### For complete API documentation, refer to the [Swagger UI](http://localhost/api/v1/docs/) after running the project.

### Authentication
```bash
POST /api/v1/auth/token/ # Obtain JWT token
POST /api/v1/auth/token/refresh/ # Refresh token
POST /api/v1/auth/token/verify/ # Verify token
```

### Users
```bash
POST /api/v1/users/ # Register new user
GET /api/v1/users/me/ # Get current user
GET /api/v1/users/search/ # Search users
```

### Messages
```bash
GET /api/v1/conversations/ # List conversations
GET /api/v1/conversations/<user_id>/messages/ # Get messages
POST /api/v1/conversations/<user_id>/messages/ # Send message
```

## Kubernetes Deployment

Deploying the Light Messages Backend on Kubernetes allows for scalable and resilient application management. This section guides you through setting up and deploying the application using Kubernetes and Minikube.

### Kubernetes Deployment Diagram
![Kubernetes Deployment Diagram](./imgs/kubernetes_architecture.png)

### Prerequisites

- **Minikube**: Runs a local Kubernetes cluster for testing. [Installation Guide](https://minikube.sigs.k8s.io/docs/start/)
- **kubectl**: Command-line tool for Kubernetes. [Installation Guide](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- **Docker**: Needed for building container images. [Installation Guide](https://docs.docker.com/get-docker/)
- **Make** (optional): Simplifies command execution using the provided Makefile. [Installation Guide](https://www.gnu.org/software/make/)

### Kubernetes Setup Instructions

1. **Start Minikube with Ingress Support**

   Begin by starting Minikube and enabling the ingress addon:

   ```bash
   make minikube-start
   ```

  Or without `make`:

  ```bash
  minikube start
  minikube addons enable ingress
  minikube tunnel
  ```

   Or manually for the first-time setup to ensure the driver is Docker, ingress is enabled, and resources are allocated properly:

   ```bash
   minikube start --driver=docker --addons=ingress --cpus=2 --memory=4096
   ```

   *Note:* Adjust the CPU and memory settings according to your machine's specifications.

2. **Use Shared Local Environment Files (Single Source of Truth)**

  Kubernetes local overlay reuses the same environment files as Docker Compose:

  ```bash
  .envs/local/.django.env
  .envs/local/.postgresql.env
  .envs/local/.nginx.env
  ```

  Notes:
  - `ADMIN_PATH` is read from `.envs/local/.nginx.env` and injected into ingress admin path.
  - In local setup, ingress host is `localhost` (no custom hosts-file mapping required).

3. **Build Local Backend Image for Minikube**

  ```bash
  make minikube-build
  ```

  Or without `make`:

  ```bash
  minikube image build -t light_messages_backend:local -f docker/django/Dockerfile --build-opt build-arg=ENVIRONMENT=local .
  ```

  This builds `light_messages_backend:local` directly inside Minikube image store.

### Deployment Commands

Deploy the Kubernetes resources using the provided manifests:

```bash
make k8s-apply
```

Or without `make`:

```bash
kubectl kustomize --load-restrictor LoadRestrictionsNone k8s/overlays/local | kubectl apply -f -
kubectl get all
```

**Why `--load-restrictor LoadRestrictionsNone`?**

Kustomize is configured to reuse shared env files from `.envs/local/` (outside `k8s/overlays/local`).
By default, Kustomize blocks loading files outside the kustomization directory, so this flag is required for local rendering in this project.

To re-apply after changes:

```bash
make k8s-reapply
```

Or without `make`:

```bash
kubectl kustomize --load-restrictor LoadRestrictionsNone k8s/overlays/local | kubectl delete -f -
kubectl kustomize --load-restrictor LoadRestrictionsNone k8s/overlays/local | kubectl apply -f -
kubectl get all
```

### Accessing the Application

Once deployed, you can access the application using the following URLs:

- **Backend API**: `http://localhost/api/v1/`
- **Admin Interface**: `http://localhost/admin_123/`
- **WebSocket**: `ws://localhost/ws/`
- **Static Files**: `http://localhost/static/`
- **Media Files**: `http://localhost/media/`

### Scaling and Management

To scale the application, use the following commands:

```bash
# Scale the backend deployment
kubectl scale deployment light-messages-web --replicas=<number-of-replicas>

# Scale the channels deployment
kubectl scale deployment light-messages-channels --replicas=<number-of-replicas>
```

To view logs for the deployments:

```bash
# View logs for the backend
make k8s-logs-web

# View logs for the channels
make k8s-logs-channels
```

Or without `make`:

```bash
# View logs for the backend
kubectl logs -l app=light-messages-web

# View logs for the channels
kubectl logs -l app=light-messages-channels
```

Access Dashboard:

```bash
minikube dashboard
```

To delete the deployment:

```bash
make k8s-delete
```

This is a safe delete and keeps persistent volumes (including PostgreSQL data PVC).

Or without `make`:

```bash
kubectl delete ingress light-messages-ingress --ignore-not-found=true
kubectl delete deployment light-messages-web light-messages-channels static-file-server postgres redis --ignore-not-found=true
kubectl delete service backend-service-web channels-service static-file-server postgres redis --ignore-not-found=true
kubectl delete configmap ingress-config --ignore-not-found=true
kubectl delete secret backend-secret --ignore-not-found=true
kubectl get all
kubectl get pvc
```

To delete everything from the local overlay including PVCs:

```bash
make k8s-delete-all
```

Or without `make`:

```bash
kubectl kustomize --load-restrictor LoadRestrictionsNone k8s/overlays/local | kubectl delete -f -
kubectl get all
kubectl get pvc
```

**Differences from Docker Compose**:

- **Scalability**: Kubernetes allows scaling of individual components horizontally.
- **Management**: Provides rolling updates and self-healing.
- **Configuration**: Uses declarative manifests (`kustomization.yaml`, `ingress.yaml`) and overlay-based customization.

### Production Note

This Kubernetes setup is intended for **local testing with Minikube**.

For production-grade deployment and infrastructure (AWS/EKS, ArgoCD, secrets management, networking, and scaling), use the dedicated IaC repository:

- https://github.com/abdelslam1997/light_messages_iac


