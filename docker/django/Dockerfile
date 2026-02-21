### Build Stage ###
ARG PYTHON_VERSION=3.12.3-slim-bookworm
FROM python:${PYTHON_VERSION} as builder

# Set working directory for build stage
WORKDIR /build

# Prevent Python from writing pyc files and ensure Python output is sent straight to terminal
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements ./requirements
ARG ENVIRONMENT=production
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r ./requirements/${ENVIRONMENT}.txt

### Final Stage ###
FROM python:${PYTHON_VERSION}

# Set working directory for the application
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder stage and install
COPY --from=builder /build/wheels /wheels
RUN pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

# Copy the application code
COPY . /app

# Copy and prepare entry point scripts
COPY ./docker/django/entrypoint.sh /entrypoint.sh
COPY ./docker/django/start.sh /start.sh

# Fix line endings and make scripts executable
RUN sed -i 's/\r$//g' /entrypoint.sh \
    && sed -i 's/\r$//g' /start.sh \
    && chmod +x /entrypoint.sh \
    && chmod +x /start.sh

# Set the entry point
ENTRYPOINT ["/entrypoint.sh"]