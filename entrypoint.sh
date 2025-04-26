#!/bin/bash
set -e

source /app/.venv/bin/activate

cd /app/testforproninteam

python manage.py migrate

python manage.py shell -c "
import os
from django.contrib.auth import get_user_model
from dotenv import load_dotenv

load_dotenv('/app/.env')

User = get_user_model()

username = os.getenv('NAME_USER')
email = os.getenv('EMAIL_HOST_USER')
password = os.getenv('EMAIL_HOST_PASSWORD')

if not username or not email or not password:
    print('Ошибка: переменные NAME_USER, EMAIL_HOST_USER или EMAIL_HOST_PASSWORD не заданы в .env')
else:
    if not User.objects.filter(username=username).exists():
        user = User.objects.create_superuser(username=username, email=email, password=password)
        print(f'Суперпользователь {username} создан.')
    else:
        print(f'Суперпользователь {username} уже существует.')
"

python manage.py fill_mock_data --users 5 --collects 10 --payments 20

echo ""
echo "Сервер Django запущен: http://localhost:8000/swagger/"

python manage.py runserver 0.0.0.0:8000
