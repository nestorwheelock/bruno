#!/bin/sh
set -e

echo "Waiting for database..."
while ! python manage.py check --database default > /dev/null 2>&1; do
    sleep 1
done

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating users..."
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='nestor').exists():
    User.objects.create_user('nestor', password='helpbruno')
    print('Created user: nestor')
if not User.objects.filter(username='alberto').exists():
    User.objects.create_user('alberto', password='helpbruno')
    print('Created user: alberto')
print('Users ready')
EOF

echo "Starting server..."
exec gunicorn --bind 0.0.0.0:8000 brunosite.wsgi:application
