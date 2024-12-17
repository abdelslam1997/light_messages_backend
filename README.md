# Light Messages Backend

## Table of Contents
- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Setup](#project-setup)
  - [Prerequisites](#prerequisites)
  - [Environment Setup](#environment-setup)
  - [Docker Compose Setup](#docker-compose-setup)
- [Development](#development)
  - [Running the Project](#running-the-project)
  - [Common Commands](#common-commands)
  - [Accessing Services](#accessing-services)
- [Testing](#testing)
- [Kubernetes Deployment](#kubernetes-deployment)
  - [Prerequisites](#prerequisites-1)
  - [Setup Instructions](#setup-instructions)
  - [Deployment Commands](#deployment-commands)
  - [Accessing the Application](#accessing-the-application)
  - [Scaling and Management](#scaling-and-management)
- [API Documentation](#api-documentation)

## Overview

Light Messages Backend is a scalable real-time messaging API built with Django. Key features:

- Real-time messaging via WebSocket connections
- RESTful API endpoints for message management
- Secure user authentication and authorization
- Horizontally scalable architecture
- Containerized deployment with Docker and Kubernetes
- Comprehensive test coverage

### Frontend Integration
Compatible with [Light Messages Frontend](https://github.com/abdelslam1997/light_messages_frontend) for a complete messaging solution.

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

## Project Setup ( Docker Compose )

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
DJANGO_SETTINGS_MODULE=config.settings.local
DJANGO_SECRET_KEY=<your-secret-key-here>
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
REDIS_URL=redis://redis:6379/0

# .envs/local/.postgresql.env
POSTGRES_DB=light_messages_db
POSTGRES_USER=light_messages_user
POSTGRES_PASSWORD=<your-db-password-here>
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# .envs/local/.nginx.env
ADMIN_PATH=admin
```

### Docker Compose Setup

Build and start services:
```bash
# Build images
make build

# Start services
make up

# View logs
make logs
```

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

## Kubernetes Deployment

Deploying the Light Messages Backend on Kubernetes allows for scalable and resilient application management. This section guides you through setting up and deploying the application using Kubernetes and Minikube.

### Prerequisites

- **Minikube**: Runs a local Kubernetes cluster for testing. [Installation Guide](https://minikube.sigs.k8s.io/docs/start/)
- **kubectl**: Command-line tool for Kubernetes. [Installation Guide](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- **Docker**: Needed for building container images. [Installation Guide](https://docs.docker.com/get-docker/)
- **Make** (optional): Simplifies command execution using the provided Makefile. [Installation Guide](https://www.gnu.org/software/make/)

### Setup Instructions

1. **Start Minikube with Ingress Support**

   Begin by starting Minikube and enabling the ingress addon:

   ```bash
   make minikube-start
   ```

   or manually for first time setup to make sure driver is docker and ingress is enabled and resources are allocated properly:

   ```bash
    minikube start --driver=docker --addons=ingress --cpus=2 --memory=4096
    ```
    note that you can adjust the cpus and memory according to your machine specs.

2. **Set Up Environment**

    Create the necessary environment files:
    create  `k8s/overlays/local/.envs` directory and create the following files:

    ```bash
    touch k8s/overlays/local/.envs/.django.env
    touch k8s/overlays/local/.envs/.postgresql.env
    touch k8s/overlays/local/.envs/.nginx.env
    ```

3. **Update host in patches.yaml**

    Update the host in `k8s/overlays/local/patches.yaml` to match your local machine hostname.

    make sure to replace `light-messages.local` with your local machine hostname or add the hostname.

    On Windows:
    ```powershell
    # View current hostname
    hostname

    # Add hostname to hosts file (Run as Administrator)
    echo "127.0.0.1 light-messages.local" >> C:\Windows\System32\drivers\etc\hosts
    ```

    On Linux:
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
kubectl scale deployment backend --replicas=<number-of-replicas>

# Scale the channels deployment
kubectl scale deployment channels --replicas=<number-of-replicas>
```

To view logs for the deployments:

```bash
# View logs for the backend
make k8s-logs-web

# View logs for the channels
make k8s-logs-channels
```

To delete the deployment:

```bash
make k8s-delete
```

## API Endpoints

#### For complete API documentation, refer to the [Swagger UI](http://localhost/api/v1/docs/).

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


