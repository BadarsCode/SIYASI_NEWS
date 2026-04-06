FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY SIYASI_NEWS /app/SIYASI_NEWS
COPY News /app/News
COPY manage.py /app/manage.py
COPY static /app/static

EXPOSE 8000

CMD ["/bin/sh", "-c", "PORT=${PORT:-8000}; python manage.py migrate --noinput && python manage.py collectstatic --noinput && exec gunicorn SIYASI_NEWS.wsgi:application --bind 0.0.0.0:${PORT} --workers 3"]
