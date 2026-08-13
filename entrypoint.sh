#!/bin/sh

set -e

# Wait for MariaDB port to open
echo "Waiting for MariaDB to be ready..."
while ! nc -z mariadb 3306; do
  sleep 1
done
echo "MariaDB is ready!"

# Apply database migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the container's CMD
exec "$@"

# Change:
exec gunicorn "$@"

# To:
exec python -m gunicorn "$@"