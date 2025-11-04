#!/bin/bash
set -e

echo "Starting database initialization..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
MAX_RETRIES=30
RETRY_COUNT=0

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -c '\q' 2>/dev/null; do
  RETRY_COUNT=$((RETRY_COUNT+1))
  if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
    echo "ERROR: PostgreSQL did not become ready in time"
    exit 1
  fi
  echo "PostgreSQL is unavailable - sleeping (attempt $RETRY_COUNT/$MAX_RETRIES)"
  sleep 2
done

echo "PostgreSQL is ready!"

# Create database if it doesn't exist
echo "Checking if database '$POSTGRES_DB' exists..."
DB_EXISTS=$(PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$POSTGRES_DB'")

if [ "$DB_EXISTS" = "1" ]; then
  echo "Database '$POSTGRES_DB' already exists"
else
  echo "Creating database '$POSTGRES_DB'..."
  PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE $POSTGRES_DB"
  echo "Database '$POSTGRES_DB' created successfully"
fi

# Enable PostGIS extension
echo "Enabling PostGIS extension..."
PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "CREATE EXTENSION IF NOT EXISTS postgis;" || true

# Run migrations if alembic.ini exists
if [ -f "alembic.ini" ]; then
  echo "Running database migrations..."
  alembic upgrade head || echo "WARNING: Migrations failed or no migrations to run"
else
  echo "No alembic.ini found, skipping migrations"
fi

echo "Database initialization complete!"
