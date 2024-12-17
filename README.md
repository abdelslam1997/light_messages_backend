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

## Kubernetes Deployment (Minikube)

### Prerequisites
- Minikube
- kubectl

### Basic Commands
```bash
# Start minikube
make minikube-restart

# Deploy application
make k8s-apply

# View logs
make k8s-logs-web
make k8s-logs-channels

# Delete deployment
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


