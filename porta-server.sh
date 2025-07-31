#!/bin/bash

PORT=8111
UVICORN_PID_FILE="porta.pid"
NGROK_PID_FILE="ngrok.pid"
NGROK_URL_FILE="ngrok.url"

start_server() {
    echo "🚀 Запуск Porta MCP на порту $PORT..."
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
    else
        echo "⚠️ Не удалось получить URL от ngrok. Возможно, он ещё инициализируется."
    fi
}

stop_server() {
    echo "🛑 Остановка Porta и ngrok..."
    if [ -f "$UVICORN_PID_FILE" ]; then
        kill -9 $(cat "$UVICORN_PID_FILE") 2>/dev/null && rm "$UVICORN_PID_FILE"
    fi
    if [ -f "$NGROK_PID_FILE" ]; then
        kill -9 $(cat "$NGROK_PID_FILE") 2>/dev/null && rm "$NGROK_PID_FILE"
    fi
    rm -f "$NGROK_URL_FILE"
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
    *)
        echo "Использование: $0 {start|stop|restart|status}"
        exit 1
esac
