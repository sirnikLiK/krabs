#!/bin/bash

# 1. Проверяем наличие npm, если его нет — устанавливаем
if ! command -v npm &> /dev/null; then
    echo "npm не найден. Устанавливаем nodejs и npm..."
    sudo apt update && sudo apt install -y nodejs npm
else
    echo "npm уже установлен."
fi

# 2. Устанавливаем Gemini CLI глобально
echo "Установка @google/gemini-cli..."
sudo npm install -g @google/gemini-cli

# 3. Проверка установки
if command -v gemini &> /dev/null; then
    echo "--------------------------------------"
    echo "Установка завершена успешно!"
    echo "Попробуйте запустить: gemini --help"
else
    echo "Что-то пошло не так. Проверьте логи установки выше."
fi