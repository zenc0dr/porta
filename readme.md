# Porta

**MCP-драйвер для Linux** - универсальный интерфейс для агентных систем.

Porta превращает любое Linux-устройство в MCP-сервер, обеспечивая безопасный и стандартизованный доступ к возможностям хоста через REST API.

## 🎯 Видение

**Porta = MCP-драйвер для Linux**

Как драйвер позволяет программам работать с железом, так Porta позволяет агентным системам работать с Linux-устройствами.

### Архитектура
```
[Агентная система] ←→ [Porta MCP Server] ←→ [Linux устройство]
     (Claude)              (porta.py)           (Raspberry Pi, VPS, etc.)
```

### Возможности
- 🧠 **Универсальный агентный интерфейс**
- 🔐 **Безопасный, стандартизованный доступ к возможностям хоста**
- ⚙️ **REST API вместо локальных скриптов и ssh-костылей**
- 🚀 **Готовность к подключению ИИ-агентов, облаков, систем мониторинга, RPA**

## 📋 Porta Minimal Agent Protocol (PMAP)

Минимальная, но самодостаточная модель взаимодействия:

| Возможность | Описание |
|-------------|----------|
| `/run_bash` | Выполнение команды, логгируя agent_id |
| `/read_file` | Чтение файла |
| `/write_file` | Запись файла |
| `/list_dir` | Обзор папки, с фильтрацией |
| `agent_id` | Поле в каждом POST-запросе |
| `X-PORTA-TOKEN` | (опционально) токен безопасности |
| `/agent/status` | Проверка работоспособности и пинга |
| `/meta`, `/public_url` | Внутренняя служебная информация Porta |

## 🚀 Установка и настройка

### ⚡ Быстрый старт (для опытных пользователей)

```bash
# Клонируем и запускаем за 30 секунд
git clone https://github.com/zenc0dr/porta.git && cd porta
python3 -m venv porta-env && source porta-env/bin/activate
pip install -r requirements.txt
python3 porta.py
```

### Предварительные требования

Перед установкой Porta убедитесь, что у вас есть:

- **Python 3.8+** - современная версия Python
- **Git** - для клонирования репозитория
- **pip** - менеджер пакетов Python
- **Linux-система** - Ubuntu, Debian, CentOS, или любое другое Linux-дистрибутив
- **ngrok** - для публичного доступа (опционально)

### Шаг 1: Клонирование репозитория

```bash
# Клонируем репозиторий с GitHub
git clone https://github.com/zenc0dr/porta.git

# Переходим в директорию проекта
cd porta
```

### Шаг 2: Создание виртуального окружения (рекомендуется)

```bash
# Создаем виртуальное окружение
python3 -m venv porta-env

# Активируем виртуальное окружение
# Для Linux/macOS:
source porta-env/bin/activate

# Для Windows:
# porta-env\Scripts\activate
```

### Шаг 3: Установка зависимостей

```bash
# Устанавливаем необходимые пакеты
pip install -r requirements.txt
```

**Устанавливаемые зависимости:**
- `fastapi` - современный веб-фреймворк для API
- `uvicorn` - ASGI-сервер для запуска FastAPI
- `pydantic` - валидация данных и сериализация

### Шаг 4: Проверка установки

```bash
# Проверяем, что Python и зависимости установлены
python3 --version
pip list | grep -E "(fastapi|uvicorn|pydantic)"
```

### Шаг 5: Установка ngrok (для публичного доступа)

```bash
# Установка ngrok через snap (Ubuntu/Debian)
sudo snap install ngrok

# Или скачать с официального сайта
# https://ngrok.com/download

# Проверка установки
ngrok version
```

## 🏃‍♂️ Запуск

### Базовый запуск

```bash
# Запускаем сервер
python3 porta.py
```

Сервер запустится на `http://localhost:5000`

### Проверка работоспособности

```bash
# Проверяем, что сервер отвечает
curl http://localhost:5000/

# Или откройте в браузере:
# http://localhost:5000/
```

### Запуск в фоновом режиме

```bash
# Запуск в фоне с логированием
nohup python3 porta.py > porta.log 2>&1 &

# Проверка процесса
ps aux | grep porta.py
```

### Остановка сервера

```bash
# Найти PID процесса
ps aux | grep porta.py

# Остановить процесс
kill <PID>

# Или если запущен в фоне:
pkill -f porta.py
```

## 🌐 Публичный доступ через ngrok

### Запуск с публичным доступом

Porta поддерживает автоматический запуск с ngrok для публичного доступа:

```bash
# Запуск Porta с ngrok (публичный доступ)
./porta-server.sh start

# Проверка статуса
./porta-server.sh status

# Остановка
./porta-server.sh stop
```

### Что происходит при запуске:

1. **Porta запускается** на порту 8111
2. **ngrok создает туннель** для публичного доступа
3. **Токен безопасности** устанавливается автоматически
4. **Публичный URL** сохраняется в файл `ngrok.url`

### Пример работы:

```bash
# Запуск
./porta-server.sh start
# 🚀 Запуск Porta MCP на порту 8111...
# 🔐 Токен безопасности установлен: test123
# 🌐 Запуск ngrok...
# ✅ MCP доступен по адресу: https://abc123.ngrok-free.app

# Проверка статуса
./porta-server.sh status
# 📊 Статус Porta MCP:
# 🟢 Porta работает (PID 12345)
# 🟢 ngrok работает (PID 12346)
# 🌍 Публичный адрес: https://abc123.ngrok-free.app
```

### Использование публичного API:

```bash
# Получение информации об API
curl -H "X-PORTA-TOKEN: test123" https://abc123.ngrok-free.app/

# Выполнение команды через интернет
curl -X POST -H "X-PORTA-TOKEN: test123" \
     -H "Content-Type: application/json" \
     -d '{"cmd": "echo Hello from internet!", "agent_id": "remote-agent"}' \
     https://abc123.ngrok-free.app/run_bash

# Управление файлами
curl -X POST -H "X-PORTA-TOKEN: test123" \
     -H "Content-Type: application/json" \
     -d '{"path": "remote_file.txt", "content": "Data from internet", "agent_id": "remote-agent"}' \
     https://abc123.ngrok-free.app/write_file
```

### Безопасность публичного доступа:

- **Токен аутентификации** обязателен для всех запросов
- **Логирование** всех операций с agent_id
- **Ограничения доступа** к файловой системе
- **Временные URL** - ngrok URLs меняются при перезапуске

### Управление ngrok:

```bash
# Проверка ngrok процесса
ps aux | grep ngrok

# Просмотр ngrok API
curl http://127.0.0.1:4040/api/tunnels

# Остановка ngrok
pkill -f ngrok

# Просмотр логов
tail -f ngrok.log
```

## 🔧 Альтернативные способы установки

### Установка через pip (если проект опубликован в PyPI)

```bash
# В будущем, когда проект будет в PyPI:
# pip install porta-mcp
```

### Установка в Docker (если есть Dockerfile)

```bash
# Клонируем репозиторий
git clone https://github.com/zenc0dr/porta.git
cd porta

# Собираем Docker-образ
docker build -t porta-mcp .

# Запускаем контейнер
docker run -p 5000:5000 porta-mcp
```

### Установка на Raspberry Pi

```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python и Git
sudo apt install python3 python3-pip python3-venv git -y

# Клонируем и устанавливаем как обычно
git clone https://github.com/zenc0dr/porta.git
cd porta
python3 -m venv porta-env
source porta-env/bin/activate
pip install -r requirements.txt
```

## 🛠️ Устранение неполадок

### Проблема: "ModuleNotFoundError: No module named 'fastapi'"

**Решение:**
```bash
# Убедитесь, что виртуальное окружение активировано
source porta-env/bin/activate

# Переустановите зависимости
pip install -r requirements.txt
```

### Проблема: "Permission denied" при запуске

**Решение:**
```bash
# Убедитесь, что файл porta.py исполняемый
chmod +x porta.py

# Или запускайте через python3
python3 porta.py
```

### Проблема: "Address already in use" (порт 5000 занят)

**Решение:**
```bash
# Найти процесс, использующий порт 5000
sudo lsof -i :5000

# Остановить процесс
sudo kill <PID>

# Или изменить порт в porta.py
```

### Проблема: "Git command not found"

**Решение:**
```bash
# Установить Git
sudo apt install git  # Ubuntu/Debian
sudo yum install git  # CentOS/RHEL
```

### Проблема: "ngrok command not found"

**Решение:**
```bash
# Установить ngrok
sudo snap install ngrok  # Ubuntu/Debian

# Или скачать вручную
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/
```

### Проблема: "ngrok tunnel offline"

**Решение:**
```bash
# Проверить статус ngrok
curl http://127.0.0.1:4040/api/tunnels

# Перезапустить ngrok
pkill -f ngrok
./porta-server.sh start

# Проверить логи
tail -f ngrok.log
```

### Проверка системных требований

```bash
# Проверка версии Python
python3 --version

# Проверка установки pip
pip --version

# Проверка установки Git
git --version

# Проверка доступности порта 5000
netstat -tuln | grep :5000

# Проверка ngrok
ngrok version
```

## API Endpoints

### GET /
Описание API и доступных методов.

### POST /run_bash
Выполняет bash-команду.

**Параметры:**
- `cmd` (string): Команда для выполнения
- `agent_id` (string, опционально): ID агента для логирования

**Пример:**
```bash
curl -X POST "http://localhost:5000/run_bash" \
     -H "Content-Type: application/json" \
     -d '{"cmd": "ls -la", "agent_id": "claude-agent-001"}'
```

**Ответ:**
```json
{
  "stdout": "вывод команды",
  "stderr": "ошибки команды", 
  "exit_code": 0,
  "success": true,
  "agent_id": "claude-agent-001"
}
```

### POST /write_file
Создает или обновляет файл на диске.

**Параметры:**
- `path` (string): Путь к файлу (абсолютный или относительный)
- `content` (string): Содержимое файла
- `agent_id` (string, опционально): ID агента для логирования

**Пример:**
```bash
curl -X POST "http://localhost:5000/write_file" \
     -H "Content-Type: application/json" \
     -d '{"path": "test_hello.txt", "content": "Привет от Элии!", "agent_id": "claude-agent-001"}'
```

**Ответ:**
```json
{
  "success": true,
  "message": "Файл успешно записан",
  "path": "/aum/projects/Porta/test_hello.txt",
  "agent_id": "claude-agent-001"
}
```

**Обработка ошибок:**
- `400 Bad Request` - Недопустимый путь (например, `/etc/passwd`)
- `500 Internal Server Error` - Системная ошибка записи файла

### POST /read_file
Читает содержимое файла с диска.

**Параметры:**
- `path` (string): Путь к файлу (абсолютный или относительный)
- `agent_id` (string, опционально): ID агента для логирования

**Пример:**
```bash
curl -X POST "http://localhost:5000/read_file" \
     -H "Content-Type: application/json" \
     -d '{"path": "test_hello.txt", "agent_id": "claude-agent-001"}'
```

**Ответ:**
```json
{
  "success": true,
  "content": "Привет от Элии!",
  "path": "/aum/projects/Porta/test_hello.txt",
  "agent_id": "claude-agent-001"
}
```

**Обработка ошибок:**
- `400 Bad Request` - Недопустимый путь или путь не является файлом
- `404 Not Found` - Файл не существует
- `500 Internal Server Error` - Системная ошибка чтения файла

### POST /list_dir
Показывает содержимое папки.

**Параметры:**
- `path` (string): Путь к папке (абсолютный или относительный)
- `include_hidden` (boolean): Включать ли скрытые файлы (по умолчанию false)
- `agent_id` (string, опционально): ID агента для логирования

**Пример:**
```bash
curl -X POST "http://localhost:5000/list_dir" \
     -H "Content-Type: application/json" \
     -d '{"path": ".", "include_hidden": false, "agent_id": "claude-agent-001"}'
```

**Ответ:**
```json
{
  "success": true,
  "entries": [
    {"name": "mcp", "type": "dir"},
    {"name": "memory-bank-data", "type": "dir"},
    {"name": "notes", "type": "dir"},
    {"name": "porta.py", "type": "file"},
    {"name": "readme.md", "type": "file"}
  ],
  "path": "/aum/projects/Porta",
  "agent_id": "claude-agent-001"
}
```

**Обработка ошибок:**
- `400 Bad Request` - Недопустимый путь или путь не является папкой
- `404 Not Found` - Папка не существует
- `500 Internal Server Error` - Системная ошибка чтения папки

### POST /agent/status
Проверка работоспособности агента.

**Параметры:**
- `agent_id` (string): ID агента

**Пример:**
```bash
curl -X POST "http://localhost:5000/agent/status" \
     -H "Content-Type: application/json" \
     -d '{"agent_id": "claude-agent-001"}'
```

**Ответ:**
```json
{
  "status": "ok",
  "agent_id": "claude-agent-001",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### GET /meta
Системная информация о Porta.

**Ответ:**
```json
{
  "name": "Porta MCP",
  "version": "1.1.0",
  "description": "MCP-драйвер для Linux",
  "uptime": "2h 15m",
  "pid": 12345,
  "port": 5000,
  "endpoints": ["/", "/run_bash", "/write_file", "/read_file", "/list_dir", "/agent/status", "/meta", "/public_url"]
}
```

### GET /public_url
Возвращает текущий публичный URL (если доступен через ngrok).

**Ответ:**
```json
{
  "public_url": "https://abc123.ngrok.io",
  "available": true
}
```

## Безопасность

⚠️ **Внимание:** Этот сервер выполняет команды в системе и записывает файлы. Используйте только в доверенной среде.

**Защита файловой системы:**
- Запрещены пути с `..` (выход из текущей директории)
- Запрещен доступ к `/etc` и `/dev`
- Файлы записываются относительно текущей директории запуска

**Агентная безопасность:**
- Логирование всех операций с agent_id
- Опциональная аутентификация через X-PORTA-TOKEN
- Аудит-трейл для мониторинга активности

## Примеры использования

### Подключение агентной системы
```bash
# Регистрация агента
curl -X POST "http://localhost:5000/agent/status" \
     -H "Content-Type: application/json" \
     -d '{"agent_id": "my-agent-001"}'

# Выполнение команды
curl -X POST "http://localhost:5000/run_bash" \
     -H "Content-Type: application/json" \
     -d '{"cmd": "echo Hello from agent", "agent_id": "my-agent-001"}'
```

### Управление файлами
```bash
# Создание файла
curl -X POST "http://localhost:5000/write_file" \
     -H "Content-Type: application/json" \
     -d '{"path": "agent_data.txt", "content": "Data from agent", "agent_id": "my-agent-001"}'

# Чтение файла
curl -X POST "http://localhost:5000/read_file" \
     -H "Content-Type: application/json" \
     -d '{"path": "agent_data.txt", "agent_id": "my-agent-001"}'
```

## Развитие проекта

Porta развивается как открытый стандарт для взаимодействия агентных систем с Linux-устройствами. Мы фокусируемся на:

- **Простоте** - минимальный, но функциональный API
- **Стандартизации** - единый протокол для всех устройств
- **Безопасности** - контролируемый доступ по умолчанию
- **Масштабируемости** - от Raspberry Pi до серверов
