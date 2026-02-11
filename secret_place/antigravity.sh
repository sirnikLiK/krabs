#!/bin/bash

# 1. Обновляем списки пакетов и устанавливаем зависимости, если их нет
echo "Проверка зависимостей (curl, gnupg)..."
sudo apt update && sudo apt install -y curl gnupg

# 2. Создаем директорию для ключей
sudo mkdir -p /etc/apt/keyrings

# 3. Скачиваем и подготавливаем ключ репозитория
echo "Настройка ключей репозитория..."
curl -fsSL https://us-central1-apt.pkg.dev/doc/repo-signing-key.gpg | \
sudo gpg --dearmor --yes -o /etc/apt/keyrings/antigravity-repo-key.gpg

# 4. Добавляем репозиторий в sources.list.d
echo "Добавление репозитория antigravity..."
echo "deb [signed-by=/etc/apt/keyrings/antigravity-repo-key.gpg] https://us-central1-apt.pkg.dev/projects/antigravity-auto-updater-dev/ antigravity-debian main" | \
sudo tee /etc/apt/sources.list.d/antigravity.list > /dev/null

# 5. Финальное обновление и установка самого приложения
echo "Установка antigravity..."
sudo apt update && sudo apt install -y antigravity

echo "Готово!"