#!/usr/bin/env sh


NAME="jusbrasil_challenge"
DJANGO_WSGI_MODULE=jusbrasil_challenge.wsgi
NUM_WORKERS=3

python manage.py makemigrations zordon
python manage.py migrate

gunicorn ${DJANGO_WSGI_MODULE}:application \
    --name ${NAME} \
    --timeout 120 \
    --workers ${NUM_WORKERS} \
    --threads 2 \
    --bind 0.0.0.0:8000 \
    --log-config gunicorn.conf \
    --log-syslog-prefix gunicorn \
    --log-level=info