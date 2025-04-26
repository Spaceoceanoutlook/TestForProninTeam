#!/bin/bash
set -e

ENV_FILE=".env"
ENV_EXAMPLE_FILE=".env.example"

echo "=== ⚙️  Подготовка окружения ==="

# Проверяем, существует ли уже .env
if [ ! -f "$ENV_FILE" ]; then
  if [ -f "$ENV_EXAMPLE_FILE" ]; then
    cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
    echo "✅ Скопирован .env.example → .env"
  else
    echo "❌ Файл .env.example не найден!"
    exit 1
  fi
else
  echo "ℹ️ Файл .env уже существует, пропускаем создание."
fi

# Запрашиваем имя пользователя
echo ""
read -p "Введите ваше имя: " NAME_USER

# Запрашиваем email
read -p "Введите ваш email: " EMAIL_HOST_USER

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

# Заполняем значения в .env
sed -i "s|^NAME_USER=.*|NAME_USER=$NAME_USER|" "$ENV_FILE" || echo "NAME_USER=$NAME_USER" >> "$ENV_FILE"
sed -i "s|^EMAIL_HOST_USER=.*|EMAIL_HOST_USER=$EMAIL_HOST_USER|" "$ENV_FILE" || echo "EMAIL_HOST_USER=$EMAIL_HOST_USER" >> "$ENV_FILE"
sed -i "s|^EMAIL_HOST_PASSWORD=.*|EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD|" "$ENV_FILE" || echo "EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD" >> "$ENV_FILE"


echo "✅ Окружение настроено!"

docker-compose up --build