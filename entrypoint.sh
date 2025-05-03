#!/bin/sh
echo "DB connection params: host=$DB_HOST user=$DB_USER dbname=$DB_NAME"
echo "Waiting for database..."
timeout 30s bash -c "while ! pg_isready -h \"$DB_HOST\" -U \"$DB_USER\"; do sleep 1; done" || { echo "Database not ready"; exit 1; }

echo "Database is ready, running migrations..."
alembic upgrade head || { echo "Migration failed"; exit 1; }

echo "Compile translations..."
pybabel compile -d bot/locales -D messages || { echo "Translation compilation failed"; exit 1; }

echo "Starting application..."
python main.py
