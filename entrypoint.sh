#!/bin/sh
set -e

# Run migrations and collectstatic
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Create superuser only if environment variables are set (and superuser doesn't exist yet)
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    echo "Creating superuser if it doesn't exist..."
    python manage.py createsuperuser --noinput || true
fi

# Execute the original command (usually your web server like gunicorn)
exec "$@"