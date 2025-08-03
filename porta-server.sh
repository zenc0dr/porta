#!/bin/bash

PORT=8111
UVICORN_PID_FILE="porta.pid"
NGROK_PID_FILE="ngrok.pid"
NGROK_URL_FILE="ngrok.url"

start_server() {
    echo "🚀 Запуск Porta MCP на порту $PORT..."
    
    # Устанавливаем токен безопасности
    export PORTA_TOKEN="test123"
    echo "🔐 Токен безопасности установлен: $PORTA_TOKEN"
    
    nohup uvicorn porta:app --host 0.0.0.0 --port $PORT > porta.log 2>&1 &
    echo $! > "$UVICORN_PID_FILE"
    sleep 2

    echo "🌐 Запуск ngrok..."
    nohup ngrok http $PORT > ngrok.log 2>&1 &
    echo $! > "$NGROK_PID_FILE"

    sleep 3

    NGROK_PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels | grep -o 'https://[0-9a-zA-Z.-]*\.ngrok-free\.app' | head -n1)
    if [ -n "$NGROK_PUBLIC_URL" ]; then
        echo "$NGROK_PUBLIC_URL" > "$NGROK_URL_FILE"
        echo "✅ MCP доступен по адресу: $NGROK_PUBLIC_URL"
        echo "💡 Примечание: При первом посещении может появиться предупреждение ngrok"
        echo "   Просто нажмите 'Visit Site' для продолжения"
    else
        echo "⚠️ Не удалось получить URL от ngrok. Возможно, он ещё инициализируется."
    fi
}

stop_server() {
    echo "🛑 Остановка Porta и ngrok..."
    
    # Остановка uvicorn
    if [ -f "$UVICORN_PID_FILE" ]; then
        PID=$(cat "$UVICORN_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill -9 $PID 2>/dev/null
            echo "✅ Porta остановлен (PID $PID)"
        else
            echo "⚠️ Porta уже не запущен"
        fi
        rm -f "$UVICORN_PID_FILE"
    else
        # Попробуем найти процесс по имени
        PIDS=$(pgrep -f "uvicorn porta:app")
        if [ -n "$PIDS" ]; then
            echo $PIDS | xargs kill -9 2>/dev/null
            echo "✅ Porta остановлен (найден по имени)"
        fi
    fi
    
    # Остановка ngrok
    if [ -f "$NGROK_PID_FILE" ]; then
        PID=$(cat "$NGROK_PID_FILE")
        if ps -p $PID > /dev/null 2>&1; then
            kill -9 $PID 2>/dev/null
            echo "✅ ngrok остановлен (PID $PID)"
        else
            echo "⚠️ ngrok уже не запущен"
        fi
        rm -f "$NGROK_PID_FILE"
    else
        # Попробуем найти процесс по имени
        PIDS=$(pgrep -f "ngrok http 8111")
        if [ -n "$PIDS" ]; then
            echo $PIDS | xargs kill -9 2>/dev/null
            echo "✅ ngrok остановлен (найден по имени)"
        fi
    fi
    
    rm -f "$NGROK_URL_FILE"
    echo "🧹 Временные файлы очищены"
}

status_server() {
    echo "📊 Статус Porta MCP:"
    if [ -f "$UVICORN_PID_FILE" ] && ps -p $(cat "$UVICORN_PID_FILE") > /dev/null; then
        echo "🟢 Porta работает (PID $(cat "$UVICORN_PID_FILE"))"
    else
        echo "🔴 Porta не запущен"
    fi

    if [ -f "$NGROK_PID_FILE" ] && ps -p $(cat "$NGROK_PID_FILE") > /dev/null; then
        echo "🟢 ngrok работает (PID $(cat "$NGROK_PID_FILE"))"
        [ -f "$NGROK_URL_FILE" ] && echo "🌍 Публичный адрес: $(cat "$NGROK_URL_FILE")"
    else
        echo "🔴 ngrok не запущен"
    fi
}

test_url() {
    if [ -f "$NGROK_URL_FILE" ]; then
        URL=$(cat "$NGROK_URL_FILE")
        echo "🧪 Тестирование URL: $URL"
        echo "📋 Результат (с пропуском предупреждения ngrok):"
        curl -H "ngrok-skip-browser-warning: true" -s "$URL" | head -c 200
        echo -e "\n..."
    else
        echo "❌ URL не найден. Запустите сервер сначала."
    fi
}

case "$1" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 1
        start_server
        ;;
    status)
        status_server
        ;;
    test)
        test_url
        ;;
    *)
        echo "Использование: $0 {start|stop|restart|status|test}"
        exit 1
esac
