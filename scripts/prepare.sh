#!/bin/bash

set -e

echo "🔎 Проверка наличия .env файла..."

if [ ! -f .env ]; then
    echo "📄 Файл .env не найден. Создаём из .env.example..."
    cp .env.example .env
else
    echo "✅ Файл .env уже существует."
fi

echo ""
echo "🔧 Настройка параметров окружения..."

# Функция для безопасной замены строк в файле .env
replace_env_var() {
    VAR_NAME=$1
    VAR_VALUE=$2
    if grep -q "^${VAR_NAME}=" .env; then
        # Заменяем существующее значение
        sed -i "s#^${VAR_NAME}=.*#${VAR_NAME}=${VAR_VALUE}#" .env
    else
        # Добавляем в конец файла
        echo "${VAR_NAME}=${VAR_VALUE}" >> .env
    fi
}

read -p "📧 Введите свой email: " email
replace_env_var "EMAIL_HOST_USER" "$email"
replace_env_var "DEFAULT_FROM_EMAIL" "$email"

read -s -p "🔑 Придумайте пароль для аккаунта: " email_password
echo ""
replace_env_var "EMAIL_HOST_PASSWORD" "$email_password"

echo ""
echo "✅ Файл .env успешно настроен."

echo ""
echo "🚀 Запуск docker-compose up --build..."
docker-compose up --build
