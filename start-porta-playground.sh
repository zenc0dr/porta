#!/bin/bash

echo "🚪 Запуск Porta Playground..."

# Проверяем, что Python установлен
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не найден. Установите Python3."
    exit 1
fi

# Проверяем зависимости
if ! python3 -c "import fastapi, uvicorn" &> /dev/null; then
    echo "📦 Устанавливаем зависимости..."
    pip3 install fastapi uvicorn
fi

# Останавливаем предыдущие процессы на порту 8111
echo "🛑 Останавливаем предыдущие процессы..."
lsof -ti:8111 | xargs kill -9 2>/dev/null || true

# Устанавливаем токен
export PORTA_TOKEN=test123

# Запускаем сервер
echo "🚀 Запускаем Porta сервер..."
python3 porta.py &
PORTA_PID=$!

# Ждем запуска сервера
echo "⏳ Ожидаем запуска сервера..."
sleep 3

# Проверяем, что сервер запустился
if curl -s -H "X-PORTA-TOKEN: test123" http://localhost:8111/meta > /dev/null; then
    echo "✅ Сервер успешно запущен!"
    echo ""
    echo "🌐 Доступные URL:"
    echo "   • Веб-интерфейс: http://localhost:8111/"
    echo "   • API документация: http://localhost:8111/docs"
    echo "   • Демо-страница: http://localhost:8111/my-porta-site.html"
    echo ""
    echo "🔑 Токен для API: test123"
    echo ""
    echo "📋 Пример команды:"
    echo "   curl -H 'X-PORTA-TOKEN: test123' http://localhost:8111/meta"
    echo ""
    echo "🛑 Для остановки нажмите Ctrl+C"
    
    # Сохраняем PID для остановки
    echo $PORTA_PID > porta.pid
    
    # Ждем сигнала остановки
    trap "echo '🛑 Останавливаем сервер...'; kill $PORTA_PID; rm -f porta.pid; exit" INT
    wait $PORTA_PID
else
    echo "❌ Ошибка запуска сервера"
    kill $PORTA_PID 2>/dev/null || true
    exit 1
fi 