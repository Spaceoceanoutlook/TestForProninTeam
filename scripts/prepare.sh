#!/bin/bash
set -e

ENV_FILE=".env"
ENV_EXAMPLE_FILE=".env.example"

echo "=== ⚙️  Подготовка окружения ==="

# Если .env существует, пропускаем настройку и сразу запускаем контейнеры
if [ -f "$ENV_FILE" ]; then
  echo "ℹ️ Файл .env уже существует, пропускаем настройку."
  docker-compose up --build
  exit 0
fi

# Проверяем, существует ли .env.example
if [ ! -f "$ENV_EXAMPLE_FILE" ]; then
  echo "❌ Файл .env.example не найден!"
  exit 1
fi

# Копируем .env.example в .env
cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
echo "✅ Скопирован .env.example → .env"

# Запрашиваем имя пользователя
echo ""
read -p "Введите ваше имя: " NAME_USER
sed -i "s|^NAME_USER=.*|NAME_USER=$NAME_USER|" "$ENV_FILE" || echo "NAME_USER=$NAME_USER" >> "$ENV_FILE"

# Запрашиваем email для аккаунта
echo ""
read -p "Введите ваш email: " EMAIL_HOST_USER
sed -i "s|^EMAIL_HOST_USER=.*|EMAIL_HOST_USER=$EMAIL_HOST_USER|" "$ENV_FILE" || echo "EMAIL_HOST_USER=$EMAIL_HOST_USER" >> "$ENV_FILE"

# Запрашиваем и проверяем пароль
while true; do
    read -s -p "Придумайте пароль: " EMAIL_HOST_PASSWORD
    echo ""

    if [ ${#EMAIL_HOST_PASSWORD} -lt 8 ]; then
        echo "Пароль должен быть не короче 8 символов."
        continue
    fi

    if [[ "$EMAIL_HOST_PASSWORD" =~ ^[0-9]+$ ]]; then
        echo "Пароль не должен состоять только из цифр."
        continue
    fi

    break
done
sed -i "s|^EMAIL_HOST_PASSWORD=.*|EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD|" "$ENV_FILE" || echo "EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD" >> "$ENV_FILE"

# Запрашиваем email для рассылок
echo ""
read -p "Введите email для рассылок: " EMAIL_FOR_NOTIFICATION
sed -i "s|^EMAIL_FOR_NOTIFICATION=.*|EMAIL_FOR_NOTIFICATION=$EMAIL_FOR_NOTIFICATION|" "$ENV_FILE" || echo "EMAIL_FOR_NOTIFICATION=$EMAIL_FOR_NOTIFICATION" >> "$ENV_FILE"

# Запрашиваем пароль для рассылок без проверки
echo ""
read -s -p "Введите пароль для рассылок: " PASSWORD_FOR_NOTIFICATION
echo ""
sed -i "s|^PASSWORD_FOR_NOTIFICATION=.*|PASSWORD_FOR_NOTIFICATION=$PASSWORD_FOR_NOTIFICATION|" "$ENV_FILE" || echo "PASSWORD_FOR_NOTIFICATION=$PASSWORD_FOR_NOTIFICATION" >> "$ENV_FILE"

echo "✅ Окружение настроено!"

# Запускаем Docker Compose
docker-compose up --build
