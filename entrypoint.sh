#!/bin/bash
set -e

source /app/.venv/bin/activate

cd /app/testforproninteam

python manage.py migrate

python manage.py createsuperuser --noinput --username test --email test@example.com || true

python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
user = User.objects.get(username='test');
user.set_password('456321Va');
user.save()"

python manage.py fill_mock_data --users 5 --collects 10 --payments 20

exec python manage.py runserver 0.0.0.0:8000