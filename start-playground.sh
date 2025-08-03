#!/bin/bash

# Porta Playground Launcher
# Скрипт для быстрого запуска Porta с веб-интерфейсом

echo "🚪 Запуск Porta Playground..."

# Проверяем, что мы в правильной директории
if [ ! -f "porta.py" ]; then
    echo "❌ Ошибка: файл porta.py не найден"
    echo "Убедитесь, что вы находитесь в директории Porta"
    exit 1
fi

# Останавливаем существующие процессы Porta
echo "🛑 Останавливаем существующие процессы Porta..."
pkill -f "uvicorn porta:app" 2>/dev/null
sleep 2

# Проверяем, что порт 8111 свободен
if lsof -Pi :8111 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Порт 8111 занят. Останавливаем процесс..."
    lsof -ti:8111 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Запускаем Porta
echo "🚀 Запускаем Porta на порту 8111..."
python3 porta.py &
PORTA_PID=$!

# Ждем запуска
echo "⏳ Ждем запуска сервера..."
sleep 5

# Проверяем, что Porta запустился
if curl -s http://localhost:8111/ > /dev/null 2>&1; then
    echo "✅ Porta успешно запущен!"
    echo ""
    echo "🌐 Porta Playground доступен по адресу:"
    echo "   http://localhost:8111/web/"
    echo ""
    echo "📋 API документация:"
    echo "   http://localhost:8111/docs"
    echo ""
    echo "🔑 Токен для API: web-agent-001"
    echo ""
    echo "💡 Для остановки нажмите Ctrl+C"
    echo ""
    
    # Сохраняем PID для корректной остановки
    echo $PORTA_PID > porta.pid
    
    # Ждем сигнала остановки
    trap 'echo ""; echo "🛑 Останавливаем Porta..."; kill $PORTA_PID; rm -f porta.pid; echo "✅ Porta остановлен"; exit 0' INT
    
    # Ждем завершения процесса
    wait $PORTA_PID
else
    echo "❌ Ошибка: Porta не запустился"
    kill $PORTA_PID 2>/dev/null
    exit 1
fi 