from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from subprocess import run, PIPE, TimeoutExpired
from typing import Optional
from datetime import datetime
import uvicorn
import logging
import os
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Porta MCP", description="Локальный интерфейс для агентов")

# Глобальная переменная для отслеживания времени запуска
START_TIME = time.time()

def get_uptime():
    """Возвращает время работы сервера в секундах"""
    return int(time.time() - START_TIME)


@app.middleware("http")
async def verify_token(request: Request, call_next):
    """Middleware для проверки X-PORTA-TOKEN заголовка"""
    expected_token = os.getenv("PORTA_TOKEN")
    token = request.headers.get("X-PORTA-TOKEN")
    
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
    """Логирует вызов агента с timestamp"""
    timestamp = datetime.now().isoformat()
    logger.info(f"[AGENT] {agent_id} called {method}: {result} at {timestamp}")


@app.get("/")
def read_root():
    return {
        "name": "Porta MCP",
        "description": "Локальный интерфейс для агентов",
        "version": "1.2.0",
        "security": "X-PORTA-TOKEN authentication enabled",
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
            }
        ]
    }


@app.get("/meta")
def get_meta():
    """Возвращает системную информацию о Porta"""
    return {
        "name": "Porta MCP",
        "version": "1.2.0",
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
            "/agent/status"
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
