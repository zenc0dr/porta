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

## Установка

```bash
pip install -r requirements.txt
```

## Запуск

```bash
python3 porta.py
```

Сервер запустится на `http://localhost:5000`

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
