#!/bin/bash

# Python script to check PostgreSQL availability
check_postgres() {
python << END
import sys
import psycopg2
import os
from psycopg2 import OperationalError

try:
    conn = psycopg2.connect(
        dbname="${POSTGRES_DB}",
        user="${POSTGRES_USER}",
        password="${POSTGRES_PASSWORD}",
        host="${POSTGRES_HOST}",
        port="${POSTGRES_PORT}",
    )
    conn.close()
except (OperationalError, psycopg2.Error) as e:
    print(f"Database connection error: {e}")
    sys.exit(1)
sys.exit(0)
END
}

until check_postgres; do
  echo "Waiting for database connection..."
  sleep 2
done

echo "Database is up - continuing..."
exec "$@"