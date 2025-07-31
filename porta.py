from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from subprocess import run, PIPE, TimeoutExpired
import uvicorn
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Porta MCP", description="Локальный интерфейс для агентов")


@app.get("/")
def read_root():
    return {
        "name": "Porta MCP",
        "description": "Локальный интерфейс для агентов",
        "version": "1.0.0",
        "methods": [
            {
                "name": "run_bash",
                "description": "Выполняет bash-команду",
                "endpoint": "/run_bash",
                "method": "POST",
                "parameters": {"cmd": "string"}
            },
            {
                "name": "write_file",
                "description": "Создает или обновляет файл",
                "endpoint": "/write_file",
                "method": "POST",
                "parameters": {"path": "string", "content": "string"}
            },
            {
                "name": "read_file",
                "description": "Читает содержимое файла",
                "endpoint": "/read_file",
                "method": "POST",
                "parameters": {"path": "string"}
            }
        ]
    }


class BashCommand(BaseModel):
    cmd: str


class FileWriteRequest(BaseModel):
    path: str
    content: str


class FileReadRequest(BaseModel):
    path: str


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
        
        return {
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "exit_code": result.returncode,
            "success": result.returncode == 0
        }
        
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
        
        return {
            "success": True,
            "message": "Файл успешно записан",
            "path": full_path
        }
        
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
            
            return {
                "success": True,
                "content": content,
                "path": full_path
            }
            
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5000)
