# План реализации PMAP (Porta Minimal Agent Protocol)

## 🎯 Цель
Реализовать Porta как MCP-драйвер для Linux с поддержкой агентных систем через PMAP протокол.

## 📋 Этапы реализации

### Этап 1: Базовая агентная поддержка ⏳

#### 1.1 Добавить agent_id во все POST endpoints
**Файл:** `porta.py`
**Задачи:**
- [ ] Добавить поле `agent_id: Optional[str] = None` в модели запросов
- [ ] Обновить `/run_bash` - добавить agent_id в BashCommand
- [ ] Обновить `/write_file` - добавить agent_id в FileWriteRequest  
- [ ] Обновить `/read_file` - добавить agent_id в FileReadRequest
- [ ] Обновить `/list_dir` - добавить agent_id в ListDirRequest
- [ ] Добавить agent_id в ответы всех endpoints

**Код:**
```python
class BashCommand(BaseModel):
    cmd: str
    agent_id: Optional[str] = None

class FileWriteRequest(BaseModel):
    path: str
    content: str
    agent_id: Optional[str] = None
```

#### 1.2 Логирование агентов
**Файл:** `porta.py`
**Задачи:**
- [ ] Создать функцию `log_agent_call(agent_id: str, method: str, result: dict)`
- [ ] Интегрировать логирование в каждый endpoint
- [ ] Добавить timestamp в логи
- [ ] Формат: `[AGENT] {agent_id} called {method}: {result}`

**Код:**
```python
def log_agent_call(agent_id: str, method: str, result: dict):
    timestamp = datetime.now().isoformat()
    logger.info(f"[AGENT] {agent_id} called {method}: {result} at {timestamp}")
```

#### 1.3 Endpoint `/agent/status`
**Файл:** `porta.py`
**Задачи:**
- [ ] Создать модель AgentStatusRequest
- [ ] Реализовать POST `/agent/status`
- [ ] Возвращать статус, agent_id, timestamp
- [ ] Логировать вызов

**Код:**
```python
@app.post("/agent/status")
async def agent_status(request: AgentStatusRequest):
    result = {
        "status": "ok",
        "agent_id": request.agent_id,
        "timestamp": datetime.now().isoformat()
    }
    log_agent_call(request.agent_id, "agent_status", result)
    return result
```

### Этап 2: Системные endpoints ⏳

#### 2.1 Endpoint `/meta`
**Файл:** `porta.py`
**Задачи:**
- [ ] Реализовать GET `/meta`
- [ ] Возвращать информацию о Porta
- [ ] Включить версию, uptime, PID, порт
- [ ] Список доступных endpoints

**Код:**
```python
@app.get("/meta")
async def get_meta():
    return {
        "name": "Porta MCP",
        "version": "1.1.0",
        "description": "MCP-драйвер для Linux",
        "uptime": get_uptime(),
        "pid": os.getpid(),
        "port": 5000,
        "endpoints": ["/", "/run_bash", "/write_file", "/read_file", "/list_dir", "/agent/status", "/meta", "/public_url"]
    }
```

#### 2.2 Endpoint `/public_url`
**Файл:** `porta.py`
**Задачи:**
- [ ] Реализовать GET `/public_url`
- [ ] Интеграция с ngrok API
- [ ] Проверка доступности ngrok
- [ ] Возврат текущего публичного URL

**Код:**
```python
@app.get("/public_url")
async def get_public_url():
    try:
        # Чтение ngrok URL из файла
        with open("ngrok.url", "r") as f:
            url = f.read().strip()
        return {"public_url": url, "available": True}
    except FileNotFoundError:
        return {"public_url": None, "available": False}
```

### Этап 3: Безопасность и токены ⏳

#### 3.1 Опциональная аутентификация
**Файл:** `porta.py`
**Задачи:**
- [ ] Добавить проверку X-PORTA-TOKEN заголовка
- [ ] Конфигурация токена через переменную окружения
- [ ] Middleware для проверки токена
- [ ] Логирование попыток доступа

**Код:**
```python
@app.middleware("http")
async def verify_token(request: Request, call_next):
    token = request.headers.get("X-PORTA-TOKEN")
    if token and token != os.getenv("PORTA_TOKEN"):
        return JSONResponse(status_code=401, content={"error": "Invalid token"})
    return await call_next(request)
```

### Этап 4: Документация и тестирование ⏳

#### 4.1 Обновление документации
**Файлы:** `readme.md`, `porta-protocol.md`
**Задачи:**
- [ ] Обновить readme.md с новыми endpoints
- [ ] Создать porta-protocol.md с описанием PMAP
- [ ] Добавить примеры использования агентов
- [ ] Документировать безопасность

#### 4.2 Тестирование
**Задачи:**
- [ ] Тестирование всех новых endpoints
- [ ] Проверка логирования агентов
- [ ] Тестирование с ngrok
- [ ] Проверка безопасности

### Этап 5: Дополнительные возможности 🔮

#### 5.1 Хранилище агентов
**Задачи:**
- [ ] SQLite база для агентов
- [ ] Fallback на agents.json
- [ ] Регистрация агентов
- [ ] Мониторинг активности

#### 5.2 Расширенный API
**Задачи:**
- [ ] `/agent/exec_pipeline` - выполнение нескольких команд
- [ ] `/agent/history` - история операций агента
- [ ] `/agent/files` - файлы агента

## 🛠️ Технические детали

### Модели данных
```python
class AgentStatusRequest(BaseModel):
    agent_id: str

class AgentResponse(BaseModel):
    success: bool
    agent_id: Optional[str] = None
    timestamp: Optional[str] = None
```

### Логирование
- Формат: `[AGENT] {agent_id} {method} {result} {timestamp}`
- Уровень: INFO
- Файл: porta.log

### Безопасность
- Токен через переменную окружения PORTA_TOKEN
- Валидация agent_id (не пустой, формат)
- Логирование всех операций

## 📊 Метрики успеха

- [ ] Все POST endpoints поддерживают agent_id
- [ ] Логирование работает для всех операций
- [ ] `/agent/status` возвращает корректный ответ
- [ ] `/meta` показывает актуальную информацию
- [ ] `/public_url` работает с ngrok
- [ ] Документация обновлена
- [ ] Тесты проходят

## 🚀 Следующие шаги

1. **Начать с Этапа 1.1** - добавить agent_id в модели
2. **Реализовать логирование** - функция log_agent_call
3. **Создать /agent/status** - базовый endpoint
4. **Протестировать** - проверить работу
5. **Добавить /meta и /public_url** - системная информация

## 💡 Принципы разработки

- **Простота** - минимальный, но функциональный API
- **Совместимость** - обратная совместимость с существующими endpoints
- **Безопасность** - логирование и валидация по умолчанию
- **Документация** - обновлять docs параллельно с кодом
