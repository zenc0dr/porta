from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from subprocess import run, PIPE, TimeoutExpired
from typing import Optional, List, Dict, Any
from datetime import datetime
import uvicorn
import logging
import os
import time
import sqlite3
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Porta MCP", description="Локальный интерфейс для агентов")

# Монтируем статические файлы
if os.path.exists("web"):
    app.mount("/web", StaticFiles(directory="web"), name="web")

# Глобальная переменная для отслеживания времени запуска
START_TIME = time.time()

# Путь к базе данных агентов
AGENTS_DB = "agents.db"

def init_agents_db():
    """Инициализирует базу данных агентов"""
    try:
        conn = sqlite3.connect(AGENTS_DB)
        cursor = conn.cursor()
        
        # Таблица агентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_operations INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Таблица операций агентов
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agent_operations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT,
                operation_type TEXT,
                details TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (agent_id) REFERENCES agents (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("База данных агентов инициализирована")
    except Exception as e:
        logger.error(f"Ошибка инициализации БД агентов: {e}")

def register_agent(agent_id: str, name: Optional[str] = None):
    """Регистрирует нового агента или обновляет существующего"""
    try:
        conn = sqlite3.connect(AGENTS_DB)
        cursor = conn.cursor()
        
        # Проверяем, существует ли агент
        cursor.execute("SELECT id FROM agents WHERE id = ?", (agent_id,))
        exists = cursor.fetchone()
        
        if exists:
            # Обновляем время последнего обращения
            cursor.execute(
                "UPDATE agents SET last_seen = CURRENT_TIMESTAMP, total_operations = total_operations + 1 WHERE id = ?",
                (agent_id,)
            )
        else:
            # Создаем нового агента
            cursor.execute(
                "INSERT INTO agents (id, name, created_at, last_seen) VALUES (?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                (agent_id, name or agent_id)
            )
        
        conn.commit()
        conn.close()
        logger.info(f"Агент {agent_id} зарегистрирован/обновлен")
    except Exception as e:
        logger.error(f"Ошибка регистрации агента {agent_id}: {e}")

def log_agent_operation(agent_id: str, operation_type: str, details: Dict[str, Any], success: bool = True):
    """Логирует операцию агента в базу данных"""
    try:
        conn = sqlite3.connect(AGENTS_DB)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO agent_operations (agent_id, operation_type, details, success) VALUES (?, ?, ?, ?)",
            (agent_id, operation_type, json.dumps(details), success)
        )
        
        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Ошибка логирования операции агента {agent_id}: {e}")

def get_uptime():
    """Возвращает время работы сервера в секундах"""
    return int(time.time() - START_TIME)

# Инициализируем базу данных при запуске
init_agents_db()


@app.middleware("http")
async def verify_token(request: Request, call_next):
    """Middleware для проверки X-PORTA-TOKEN заголовка"""
    expected_token = os.getenv("PORTA_TOKEN")
    token = request.headers.get("X-PORTA-TOKEN")
    
    # Пропускаем проверку для статических файлов
    if request.url.path.startswith("/web/"):
        return await call_next(request)
    
    # Если токен не настроен, пропускаем проверку
    if not expected_token:
        return await call_next(request)
    
    # Если токен настроен, но не передан - отказываем в доступе
    if not token:
        logger.warning(f"Попытка доступа без токена: {request.url}")
        return JSONResponse(
            status_code=401, 
            content={"error": "Missing X-PORTA-TOKEN header"}
        )
    
    # Если токен неверный - отказываем в доступе
    if token != expected_token:
        logger.warning(f"Попытка доступа с неверным токеном: {request.url}")
        return JSONResponse(
            status_code=401, 
            content={"error": "Invalid token"}
        )
    
    # Токен верный - пропускаем запрос
    return await call_next(request)


def log_agent_call(agent_id: str, method: str, result: dict):
    """Логирует вызов агента с timestamp и в базу данных"""
    timestamp = datetime.now().isoformat()
    logger.info(f"[AGENT] {agent_id} called {method}: {result} at {timestamp}")
    
    # Регистрируем агента и логируем операцию
    if agent_id:
        register_agent(agent_id)
        log_agent_operation(agent_id, method, result)


@app.get("/")
def read_root(request: Request):
    """Умный корневой эндпоинт: возвращает HTML для браузера, JSON для API"""
    
    # Проверяем User-Agent для определения типа клиента
    user_agent = request.headers.get("user-agent", "").lower()
    
    # Если это браузер (содержит browser-специфичные строки)
    if any(browser in user_agent for browser in ["mozilla", "chrome", "safari", "firefox", "edge", "opera"]):
        # Возвращаем HTML страницу Porta Playground
        try:
            with open("web/index.html", "r", encoding="utf-8") as f:
                html_content = f.read()
            return HTMLResponse(content=html_content, media_type="text/html")
        except FileNotFoundError:
            return HTMLResponse(content="<h1>Porta Playground не найден</h1>", media_type="text/html")
    
    # Для API клиентов возвращаем JSON
    return {
        "name": "Porta MCP",
        "description": "Локальный интерфейс для агентов",
        "version": "1.3.0",
        "security": "X-PORTA-TOKEN authentication enabled",
        "playground_url": "/web/",
        "methods": [
            {
                "name": "run_bash",
                "description": "Выполняет bash-команду",
                "endpoint": "/run_bash",
                "method": "POST",
                "parameters": {"cmd": "string", "agent_id": "string (optional)"}
            },
            {
                "name": "write_file",
                "description": "Создает или обновляет файл",
                "endpoint": "/write_file",
                "method": "POST",
                "parameters": {"path": "string", "content": "string", "agent_id": "string (optional)"}
            },
            {
                "name": "read_file",
                "description": "Читает содержимое файла",
                "endpoint": "/read_file",
                "method": "POST",
                "parameters": {"path": "string", "agent_id": "string (optional)"}
            },
            {
                "name": "list_dir",
                "description": "Показывает содержимое папки",
                "endpoint": "/list_dir",
                "method": "POST",
                "parameters": {"path": "string", "include_hidden": "boolean", "agent_id": "string (optional)"}
            },
            {
                "name": "agent_status",
                "description": "Проверка работоспособности агента",
                "endpoint": "/agent/status",
                "method": "POST",
                "parameters": {"agent_id": "string"}
            },
            {
                "name": "agent_list",
                "description": "Список зарегистрированных агентов",
                "endpoint": "/agent/list",
                "method": "POST",
                "parameters": {"limit": "int (optional)", "offset": "int (optional)", "status": "string (optional)"}
            },
            {
                "name": "agent_history",
                "description": "История операций агента",
                "endpoint": "/agent/history",
                "method": "POST",
                "parameters": {"agent_id": "string", "limit": "int (optional)", "operation_type": "string (optional)"}
            },
            {
                "name": "agent_pipeline",
                "description": "Выполнение последовательности команд",
                "endpoint": "/agent/pipeline",
                "method": "POST",
                "parameters": {"agent_id": "string", "commands": "array", "timeout": "int (optional)"}
            }
        ]
    }


@app.get("/meta")
def get_meta():
    """Возвращает системную информацию о Porta"""
    return {
        "name": "Porta MCP",
        "version": "1.3.0",
        "description": "MCP-драйвер для Linux",
        "uptime": get_uptime(),
        "pid": os.getpid(),
        "port": 8111,  # Фактический порт работы
        "security": "X-PORTA-TOKEN authentication enabled",
        "endpoints": [
            "/",
            "/meta", 
            "/public_url",
            "/run_bash", 
            "/write_file", 
            "/read_file", 
            "/list_dir", 
            "/agent/status",
            "/agent/list",
            "/agent/history",
            "/agent/pipeline"
        ],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/public_url")
def get_public_url():
    """Возвращает публичный URL через ngrok"""
    try:
        # Проверяем существование файла ngrok.url
        if os.path.exists("ngrok.url"):
            with open("ngrok.url", "r") as f:
                url = f.read().strip()
            return {
                "public_url": url, 
                "available": True,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "public_url": None, 
                "available": False,
                "message": "ngrok.url файл не найден",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Ошибка чтения ngrok URL: {str(e)}")
        return {
            "public_url": None, 
            "available": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


class BashCommand(BaseModel):
    cmd: str
    agent_id: Optional[str] = None


class FileWriteRequest(BaseModel):
    path: str
    content: str
    agent_id: Optional[str] = None


class FileReadRequest(BaseModel):
    path: str
    agent_id: Optional[str] = None


class DirListRequest(BaseModel):
    path: str
    include_hidden: bool = False
    agent_id: Optional[str] = None


class AgentStatusRequest(BaseModel):
    agent_id: str

class AgentListRequest(BaseModel):
    limit: Optional[int] = 50
    offset: Optional[int] = 0
    status: Optional[str] = None

class AgentHistoryRequest(BaseModel):
    agent_id: str
    limit: Optional[int] = 20
    operation_type: Optional[str] = None

class AgentPipelineRequest(BaseModel):
    agent_id: str
    commands: List[str]
    timeout: Optional[int] = 30


@app.post("/agent/status")
def agent_status(request: AgentStatusRequest):
    """Проверка работоспособности агента"""
    result = {
        "status": "ok",
        "agent_id": request.agent_id,
        "timestamp": datetime.now().isoformat()
    }
    log_agent_call(request.agent_id, "agent_status", result)
    return result


@app.post("/run_bash")
def run_bash(command: BashCommand):
    try:
        logger.info(f"Выполняется команда: {command.cmd}")
        
        # Выполняем команду с таймаутом 30 секунд
        result = run(
            command.cmd, 
            shell=True, 
            stdout=PIPE, 
            stderr=PIPE, 
            text=True,
            timeout=30
        )
        
        response = {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
            "success": result.returncode == 0
        }
        
        # Добавляем agent_id в ответ если он был передан
        if command.agent_id:
            response["agent_id"] = command.agent_id
            log_agent_call(command.agent_id, "run_bash", response)
        
        return response
        
    except TimeoutExpired:
        logger.error(f"Команда превысила таймаут: {command.cmd}")
        raise HTTPException(status_code=408, detail="Команда превысила таймаут (30 секунд)")
        
    except Exception as e:
        logger.error(f"Ошибка выполнения команды: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка выполнения команды: {str(e)}")


@app.post("/write_file")
def write_file(req: FileWriteRequest):
    try:
        logger.info(f"Запись файла: {req.path}")
        
        # Простейшая защита от доступа вне текущей директории
        if ".." in req.path or req.path.startswith("/etc") or req.path.startswith("/dev"):
            logger.error(f"Недопустимый путь: {req.path}")
            raise HTTPException(status_code=400, detail="Недопустимый путь")
        
        # Получаем абсолютный путь
        full_path = os.path.abspath(req.path)
        
        # Создаем директории если их нет
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        # Записываем файл
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(req.content)
        
        logger.info(f"Файл успешно записан: {full_path}")
        
        response = {
            "success": True,
            "message": "Файл успешно записан",
            "path": full_path
        }
        
        # Добавляем agent_id в ответ если он был передан
        if req.agent_id:
            response["agent_id"] = req.agent_id
            log_agent_call(req.agent_id, "write_file", response)
        
        return response
        
    except HTTPException:
        # Перебрасываем HTTP исключения как есть
        raise
        
    except Exception as e:
        logger.error(f"Ошибка записи файла: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка записи файла: {str(e)}")


@app.post("/read_file")
def read_file(req: FileReadRequest):
    try:
        logger.info(f"Чтение файла: {req.path}")
        
        # Проверка безопасности пути
        if ".." in req.path or req.path.startswith("/etc") or req.path.startswith("/dev"):
            logger.error(f"Недопустимый путь: {req.path}")
            raise HTTPException(status_code=400, detail="Недопустимый путь")
        
        # Получаем абсолютный путь
        full_path = os.path.abspath(req.path)
        
        # Проверяем существование файла
        if not os.path.exists(full_path):
            logger.error(f"Файл не существует: {full_path}")
            raise HTTPException(status_code=404, detail="Файл не найден")
        
        # Проверяем, что это файл, а не директория
        if not os.path.isfile(full_path):
            logger.error(f"Путь не является файлом: {full_path}")
            raise HTTPException(status_code=400, detail="Указанный путь не является файлом")
        
        # Читаем файл
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            logger.info(f"Файл успешно прочитан: {full_path}")
            
            response = {
                "success": True,
                "content": content,
                "path": full_path
            }
            
            # Добавляем agent_id в ответ если он был передан
            if req.agent_id:
                response["agent_id"] = req.agent_id
                log_agent_call(req.agent_id, "read_file", response)
            
            return response
            
        except UnicodeDecodeError:
            logger.error(f"Ошибка кодировки файла: {full_path}")
            raise HTTPException(status_code=500, detail="Ошибка чтения файла: неверная кодировка")
        except PermissionError:
            logger.error(f"Нет прав на чтение файла: {full_path}")
            raise HTTPException(status_code=500, detail="Нет прав на чтение файла")
        
    except HTTPException:
        # Перебрасываем HTTP исключения как есть
        raise
        
    except Exception as e:
        logger.error(f"Ошибка чтения файла: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка чтения файла: {str(e)}")


@app.post("/list_dir")
def list_dir(req: DirListRequest):
    try:
        logger.info(f"Чтение содержимого папки: {req.path}")
        
        # Проверка безопасности пути
        if ".." in req.path or req.path.startswith("/etc") or req.path.startswith("/dev") or req.path.startswith("/proc"):
            logger.error(f"Недопустимый путь: {req.path}")
            raise HTTPException(status_code=400, detail="Недопустимый путь")
        
        # Получаем абсолютный путь
        full_path = os.path.abspath(req.path)
        
        # Проверяем существование директории
        if not os.path.exists(full_path):
            logger.error(f"Папка не существует: {full_path}")
            raise HTTPException(status_code=404, detail="Папка не найдена")
        
        # Проверяем, что это директория, а не файл
        if not os.path.isdir(full_path):
            logger.error(f"Путь не является папкой: {full_path}")
            raise HTTPException(status_code=400, detail="Указанный путь не является папкой")
        
        # Читаем содержимое директории
        try:
            entries = []
            for item in os.listdir(full_path):
                # Пропускаем скрытые файлы, если не запрошены
                if not req.include_hidden and item.startswith('.'):
                    continue
                
                item_path = os.path.join(full_path, item)
                entry_type = "dir" if os.path.isdir(item_path) else "file"
                
                entries.append({
                    "name": item,
                    "type": entry_type
                })
            
            # Сортируем: сначала папки, потом файлы, по алфавиту
            entries.sort(key=lambda x: (x["type"] != "dir", x["name"].lower()))
            
            logger.info(f"Папка успешно прочитана: {full_path}, найдено {len(entries)} элементов")
            
            response = {
                "success": True,
                "entries": entries,
                "path": full_path
            }
            
            # Добавляем agent_id в ответ если он был передан
            if req.agent_id:
                response["agent_id"] = req.agent_id
                log_agent_call(req.agent_id, "list_dir", response)
            
            return response
            
        except PermissionError:
            logger.error(f"Нет прав на чтение папки: {full_path}")
            raise HTTPException(status_code=500, detail="Нет прав на чтение папки")
        
    except HTTPException:
        # Перебрасываем HTTP исключения как есть
        raise
        
    except Exception as e:
        logger.error(f"Ошибка чтения папки: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ошибка чтения папки: {str(e)}")


@app.post("/agent/list")
def agent_list(request: AgentListRequest):
    """Возвращает список зарегистрированных агентов"""
    try:
        conn = sqlite3.connect(AGENTS_DB)
        cursor = conn.cursor()
        
        # Формируем запрос с фильтрами
        query = "SELECT id, name, created_at, last_seen, total_operations, status FROM agents"
        params = []
        
        if request.status:
            query += " WHERE status = ?"
            params.append(request.status)
        
        query += " ORDER BY last_seen DESC LIMIT ? OFFSET ?"
        params.extend([request.limit, request.offset])
        
        cursor.execute(query, params)
        agents = []
        
        for row in cursor.fetchall():
            agents.append({
                "id": row[0],
                "name": row[1],
                "created_at": row[2],
                "last_seen": row[3],
                "total_operations": row[4],
                "status": row[5]
            })
        
        conn.close()
        
        result = {
            "success": True,
            "agents": agents,
            "total": len(agents),
            "limit": request.limit,
            "offset": request.offset
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка получения списка агентов: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения списка агентов: {str(e)}")


@app.post("/agent/history")
def agent_history(request: AgentHistoryRequest):
    """Возвращает историю операций агента"""
    try:
        conn = sqlite3.connect(AGENTS_DB)
        cursor = conn.cursor()
        
        # Формируем запрос с фильтрами
        query = "SELECT operation_type, details, timestamp, success FROM agent_operations WHERE agent_id = ?"
        params = [request.agent_id]
        
        if request.operation_type:
            query += " AND operation_type = ?"
            params.append(request.operation_type)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(request.limit)
        
        cursor.execute(query, params)
        operations = []
        
        for row in cursor.fetchall():
            try:
                details = json.loads(row[1]) if row[1] else {}
            except:
                details = {"raw": row[1]}
            
            operations.append({
                "operation_type": row[0],
                "details": details,
                "timestamp": row[2],
                "success": bool(row[3])
            })
        
        conn.close()
        
        result = {
            "success": True,
            "agent_id": request.agent_id,
            "operations": operations,
            "total": len(operations)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Ошибка получения истории агента {request.agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка получения истории агента: {str(e)}")


@app.post("/agent/pipeline")
def agent_pipeline(request: AgentPipelineRequest):
    """Выполняет последовательность команд для агента"""
    try:
        logger.info(f"Выполнение pipeline для агента {request.agent_id}: {len(request.commands)} команд")
        
        results = []
        start_time = time.time()
        
        for i, cmd in enumerate(request.commands):
            try:
                # Выполняем команду
                process = run(cmd, shell=True, capture_output=True, text=True, timeout=request.timeout)
                
                result = {
                    "command": cmd,
                    "index": i,
                    "success": process.returncode == 0,
                    "stdout": process.stdout,
                    "stderr": process.stderr,
                    "returncode": process.returncode
                }
                
                results.append(result)
                
                # Если команда завершилась с ошибкой, останавливаем pipeline
                if process.returncode != 0:
                    logger.warning(f"Команда {i+1} завершилась с ошибкой: {cmd}")
                    break
                    
            except TimeoutExpired:
                logger.error(f"Таймаут команды {i+1}: {cmd}")
                results.append({
                    "command": cmd,
                    "index": i,
                    "success": False,
                    "error": "timeout",
                    "returncode": -1
                })
                break
                
            except Exception as e:
                logger.error(f"Ошибка выполнения команды {i+1}: {cmd} - {e}")
                results.append({
                    "command": cmd,
                    "index": i,
                    "success": False,
                    "error": str(e),
                    "returncode": -1
                })
                break
        
        execution_time = time.time() - start_time
        
        response = {
            "success": all(r["success"] for r in results),
            "agent_id": request.agent_id,
            "total_commands": len(request.commands),
            "executed_commands": len(results),
            "execution_time": execution_time,
            "results": results
        }
        
        # Логируем операцию агента
        log_agent_call(request.agent_id, "pipeline", response)
        
        return response
        
    except Exception as e:
        logger.error(f"Ошибка выполнения pipeline для агента {request.agent_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка выполнения pipeline: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8111)
