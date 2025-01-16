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
  - Uses `local_docker_compose.yml`, `Dockerfile`, and `nginx.conf.template` for configuration.
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
  - **`local_docker_compose.yml`**: Defines services, volumes, and networks.
  - **`Dockerfile`**: Specifies how to build the Docker image for the Django application.
  - **`nginx.conf.template`**: Configures Nginx within the Docker container.

**Steps**:

1. **Build and Start Services**:
   ```bash
   make build
   make up
   ```

2. **Apply Migrations and Create Superuser**:
   ```bash
   make migrate
   make create-superuser
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

Make Migrations:
```bash
make makemigrations
```
Run database migrations:
```bash
make migrate
```

Create superuser:
```bash
make create-superuser
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

   Or manually for the first-time setup to ensure the driver is Docker, ingress is enabled, and resources are allocated properly:

   ```bash
   minikube start --driver=docker --addons=ingress --cpus=2 --memory=4096
   ```

   *Note:* Adjust the CPU and memory settings according to your machine's specifications.

2. **Set Up Environment**

   Create the necessary environment files:

   ```bash
   mkdir -p k8s/overlays/local/.envs
   touch k8s/overlays/local/.envs/.django.env
   touch k8s/overlays/local/.envs/.postgresql.env
   touch k8s/overlays/local/.envs/.nginx.env
   ```
  Fill the environment files with the following content:

  ```bash
  # k8s/overlays/local/.envs/.django.env
  SECRET=your_secret_key_here
  DJANGO_SETTINGS_MODULE=light_messages.settings.local
  ALLOWED_HOSTS=*
  DEBUG=true
  ADMIN_URL=admin_123/
  CORS_ALLOWED_ORIGINS=http://localhost:5173,
  REDIS_HOST=redis-service
  REDIS_PORT=6379

  # k8s/overlays/local/.envs/.postgresql.env
  POSTGRES_HOST=postgres-service
  POSTGRES_PORT=5432
  POSTGRES_DB=light_messages_db
  POSTGRES_USER=light_messages_user
  POSTGRES_PASSWORD=Pass123456
  DATABASE_URL=postgres://light_messages_user:Pass123456@postgres-service:5432/light_messages_db

  # k8s/overlays/local/.envs/.nginx.env
  ADMIN_PATH=admin_123
  ```

3. **Update Host in `patches.yaml`**

   Update the host in `k8s/overlays/local/patches.yaml` to match your local machine hostname.

   Ensure to replace `light-messages.local` with your local machine hostname or add the hostname to your hosts file.

   **On Windows:**

   ```powershell
   # View current hostname
   hostname

   # Add hostname to hosts file (Run as Administrator)
   echo "127.0.0.1 light-messages.local" >> C:\Windows\System32\drivers\etc\hosts
   ```

   **On Linux/MacOS:**

   ```bash
   # View current hostname
   hostname

   # Add hostname to hosts file
   sudo sh -c 'echo "127.0.0.1 light-messages.local" >> /etc/hosts'
   ```

### Deployment Commands

Deploy the Kubernetes resources using the provided manifests:

```bash
make k8s-apply
```

### Accessing the Application

Once deployed, you can access the application using the following URLs:

- **Backend API**: `http://<minikube-ip>/api/v1/`
- **Admin Interface**: `http://<minikube-ip>/admin/`
- **WebSocket**: `ws://<minikube-ip>/ws/`

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

Access Dashboard:

```bash
minikube dashboard
```

To delete the deployment:

```bash
make k8s-delete
```

### Setup Instructions

The Kubernetes setup provides a scalable and robust deployment suitable for production.

- **Configuration Files**:
  - **`kustomization.yaml`**: Aggregates Kubernetes manifests and applies configurations.
  - **`ingress.yaml`**: Manages external access via Ingress resources.

**Key Components**:

- Deployments for the Django application, Channels worker, PostgreSQL, and Redis.
- Services to expose deployments internally.
- Ingress controller for external access.

**Steps**:

1. **Start Minikube with Ingress Support**:
   ```bash
   make minikube-start
   ```

2. **Deploy Application to Kubernetes**:
   ```bash
   make k8s-apply
   ```

3. **Access Services**:
   - Obtain Minikube IP:
     ```bash
     minikube ip
     ```
   - API: http://minikube-ip/api/v1/
   - Admin Interface: http://minikube-ip/admin/
   - WebSocket: ws://minikube-ip/ws/

**Differences from Docker Compose**:

- **Scalability**: Kubernetes allows scaling of individual components horizontally.
- **Management**: Provides advanced features like rolling updates and self-healing.
- **Configuration**: Uses declarative manifests (`kustomization.yaml`, `ingress.yaml`) for infrastructure as code.


