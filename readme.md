# Porta

Локальный MCP-сервер для безопасного взаимодействия агентных ИИ с системой.

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

**Пример:**
```bash
curl -X POST "http://localhost:5000/run_bash" \
     -H "Content-Type: application/json" \
     -d '{"cmd": "ls -la"}'
```

**Ответ:**
```json
{
  "stdout": "вывод команды",
  "stderr": "ошибки команды", 
  "exit_code": 0,
  "success": true
}
```

### POST /write_file
Создает или обновляет файл на диске.

**Параметры:**
- `path` (string): Путь к файлу (абсолютный или относительный)
- `content` (string): Содержимое файла

**Пример:**
```bash
curl -X POST "http://localhost:5000/write_file" \
     -H "Content-Type: application/json" \
     -d '{"path": "test_hello.txt", "content": "Привет от Элии!"}'
```

**Ответ:**
```json
{
  "success": true,
  "message": "Файл успешно записан",
  "path": "/aum/projects/Porta/test_hello.txt"
}
```

**Обработка ошибок:**
- `400 Bad Request` - Недопустимый путь (например, `/etc/passwd`)
- `500 Internal Server Error` - Системная ошибка записи файла

### POST /read_file
Читает содержимое файла с диска.

**Параметры:**
- `path` (string): Путь к файлу (абсолютный или относительный)

**Пример:**
```bash
curl -X POST "http://localhost:5000/read_file" \
     -H "Content-Type: application/json" \
     -d '{"path": "test_hello.txt"}'
```

**Ответ:**
```json
{
  "success": true,
  "content": "Привет от Элии!",
  "path": "/aum/projects/Porta/test_hello.txt"
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

**Пример:**
```bash
curl -X POST "http://localhost:5000/list_dir" \
     -H "Content-Type: application/json" \
     -d '{"path": ".", "include_hidden": false}'
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
  "path": "/aum/projects/Porta"
}
```

**Обработка ошибок:**
- `400 Bad Request` - Недопустимый путь или путь не является папкой
- `404 Not Found` - Папка не существует
- `500 Internal Server Error` - Системная ошибка чтения папки

## Безопасность

⚠️ **Внимание:** Этот сервер выполняет команды в системе и записывает файлы. Используйте только в доверенной среде.

**Защита файловой системы:**
- Запрещены пути с `..` (выход из текущей директории)
- Запрещен доступ к `/etc` и `/dev`
- Файлы записываются относительно текущей директории запуска
