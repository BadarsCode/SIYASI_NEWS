#!/bin/sh
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Set default port if not provided by Railway
PORT=${PORT:-8080}

# Execute gunicorn with the proper port
exec gunicorn SIYASI_NEWS.wsgi:application --bind 0.0.0.0:$PORT
