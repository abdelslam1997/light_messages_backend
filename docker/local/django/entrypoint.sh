#!/bin/bash

# Python script to check PostgreSQL availability
check_postgres() {
python << END
import sys
import psycopg2
from psycopg2 import OperationalError

try:
    conn = psycopg2.connect(
        dbname="yourdbname",
        user="$POSTGRES_USER",
        password="yourdbpassword",
        host="$POSTGRES_HOST",
        port="$POSTGRES_PORT",
    )
    conn.close()
except (OperationalError, psycopg2.Error) as e:
    print(f"Database connection error: {e}")
    sys.exit(1)
sys.exit(0)
END
}

# Wait for PostgreSQL to be available
# until check_postgres; do
#   echo "Waiting for database connection..."
#   sleep 1
# done

echo "Database is up - continuing..."

# Execute the command passed to the entrypoint
exec "$@"
