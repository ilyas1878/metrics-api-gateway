#!/bin/bash

# Скрипт имитации CI/CD пайплайна
echo "🔄 1. Обновляем код из Git (git pull)..."
git pull origin main

echo "🛑 2. Останавливаем старые контейнеры..."
docker-compose down

echo "🚀 3. Собираем и запускаем новые контейнеры..."
docker-compose up -d --build

echo "✅ 4. Деплой завершен! API доступно по адресу: http://localhost:8000/docs"