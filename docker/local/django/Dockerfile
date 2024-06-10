
### Define Base Image
ARG PYTHON_VERSION=3.12.3-slim-bookworm
FROM python:${PYTHON_VERSION} as python-base-image

## 1. Build Stage
FROM python-base-image as build-stage
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev &&\
    rm -rf /var/lib/apt/lists/*

COPY ./requirements ./requirements
RUN pip wheel --no-cache-dir --no-deps --wheel-dir \
    /app/wheels -r ./requirements/local.txt


## 2. Run Stage
FROM python-base-image as run-stage

WORKDIR /app

COPY --from=build-stage /app/wheels /wheels
COPY --from=build-stage /app/requirements/local.txt .

RUN apt-get update && apt-get install --no-install-recommends -y \
    libpq-dev \
    gettext &&\
    rm -rf /var/lib/apt/lists/*


RUN pip install --no-cache /wheels/* && \
    rm -rf /wheels

COPY ./docker/local/django/entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//g' /entrypoint.sh && \
    chmod +x /entrypoint.sh

COPY ./docker/local/django/start.sh /start.sh
RUN sed -i 's/\r$//g' /start.sh && \
chmod +x /start.sh

# ENTRYPOINT: The command that is run when the container starts
ENTRYPOINT ["/entrypoint.sh"]