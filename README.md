# 🚪 Porta - Агентный Интерфейс

**Porta** — локальный интерфейс для взаимодействия агентов с Linux-системой через MCP (Model Context Protocol).

## 🌟 Особенности

- **🔐 Безопасность** — токен-аутентификация
- **⚡ Быстрота** — FastAPI backend
- **🎨 Красивый UI** — современный веб-интерфейс
- **📁 Работа с файлами** — чтение, запись, навигация
- **🧠 Memory Bank** — интеграция с системой памяти
- **📊 Мониторинг** — отслеживание активности агентов

## 📦 Установка

### Системные требования
- **Python 3.7+** — для запуска FastAPI приложения
- **pip3** — для установки зависимостей
- **ngrok** — для публичного доступа (опционально)
- **bash** — для выполнения скриптов управления

### Клонирование репозитория
```bash
# Клонировать репозиторий
git clone https://github.com/zenc0dr/porta
cd porta

# Или если репозиторий уже есть
cd /path/to/porta
```

### Установка зависимостей
```bash
# Установить Python зависимости
pip3 install -r requirements.txt

# Проверить установку
python3 -c "import fastapi, uvicorn; print('✅ Зависимости установлены')"
```

### Настройка окружения
```bash
# Установить токен безопасности (опционально)
export PORTA_TOKEN=your_secret_token

# Или оставить по умолчанию
export PORTA_TOKEN=test123
```

### Установка ngrok (опционально)
```bash
# Установить ngrok для публичного доступа
# Скачать с https://ngrok.com/download

# Или через snap (Ubuntu/Debian)
sudo snap install ngrok

# Или через Homebrew (macOS)
brew install ngrok

# Проверить установку
ngrok version
```

### Проверка установки
```bash
# Проверить что все файлы на месте
ls -la porta.py porta-server.sh web/index.html

# Проверить права на выполнение скрипта
chmod +x porta-server.sh

# Проверить Python зависимости
python3 -c "import fastapi, uvicorn, pydantic; print('✅ Все зависимости установлены')"

### Первый запуск
```bash
# Запустить сервер
./porta-server.sh start

# Проверить статус
./porta-server.sh status

# Открыть в браузере
# http://localhost:8111/ - главная страница
# http://localhost:8111/web/ - веб-интерфейс
```

## 🚀 Быстрый старт

### Запуск через скрипт (рекомендуется)
```bash
# Запуск сервера
./porta-server.sh start

# Проверка статуса
./porta-server.sh status

# Остановка сервера
./porta-server.sh stop

# Перезапуск
./porta-server.sh restart
```

### Ручной запуск
```bash
# Установка зависимостей
pip3 install -r requirements.txt

# Установка переменных окружения
export PORTA_TOKEN=test123

# Запуск сервера
python3 porta.py
```

### Конфигурация
Скрипт `porta-server.sh` автоматически:
- Устанавливает токен безопасности `PORTA_TOKEN=test123`
- Запускает uvicorn на порту 8111
- Запускает ngrok для публичного доступа
- Сохраняет PID процессов для управления

## 🌐 Доступные URL

- **Веб-интерфейс**: http://localhost:8111/
- **API документация**: http://localhost:8111/docs
- **Публичный URL**: http://localhost:8111/public_url

## 🔑 API Endpoints

### Основные методы
| Метод | Endpoint | Описание |
|-------|----------|----------|
| `GET` | `/` | Главная страница |
| `GET` | `/meta` | Системная информация |
| `POST` | `/run_bash` | Выполнение bash-команд |
| `POST` | `/write_file` | Создание/обновление файлов |
| `POST` | `/read_file` | Чтение файлов |
| `POST` | `/list_dir` | Просмотр директорий |

### Агентные методы
| Метод | Endpoint | Описание |
|-------|----------|----------|
| `POST` | `/agent/status` | Статус агента |
| `POST` | `/agent/list` | Список агентов |
| `POST` | `/agent/history` | История операций |
| `POST` | `/agent/pipeline` | Выполнение последовательности команд |

## 📝 Примеры использования

### Выполнение команды
```bash
curl -H "X-PORTA-TOKEN: test123" \
     -H "Content-Type: application/json" \
     -d '{"cmd": "echo Hello from agent", "agent_id": "test123"}' \
     http://localhost:8111/run_bash
```

### Создание файла
```bash
curl -H "X-PORTA-TOKEN: test123" \
     -H "Content-Type: application/json" \
     -d '{"path": "test.txt", "content": "Hello World", "agent_id": "test123"}' \
     http://localhost:8111/write_file
```

## 🎨 Веб-интерфейс

Porta Playground предоставляет удобный веб-интерфейс с:
- **Готовые команды** — быстрый доступ к популярным операциям
- **Работа с файлами** — создание, чтение, навигация через UI
- **Журнал вызовов** — полная история операций
- **Системная информация** — мониторинг в реальном времени

## 🔧 Конфигурация

### Переменные окружения
| Переменная | Описание | По умолчанию | Обязательная |
|------------|----------|--------------|--------------|
| `PORTA_TOKEN` | Токен для аутентификации | `test123` | Да |
| `PORT` | Порт сервера | `8111` | Нет |

### База данных
Система автоматически создает SQLite базу данных `agents.db` для:
- Регистрации агентов
- Логирования операций
- Отслеживания статистики

## 🛠️ Разработка

### Структура проекта
```
Porta/
├── porta.py                    # Основной сервер
├── porta-server.sh            # Скрипт управления
├── web/                       # Веб-интерфейс
│   └── index.html            # Главная страница
├── memory-bank-data/          # Данные Memory Bank
├── scripts/                  # Вспомогательные скрипты
└── tests/                    # Тесты
```

### Зависимости
- `fastapi` — веб-фреймворк
- `uvicorn` — ASGI сервер
- `pydantic` — валидация данных

## 🚀 Управление сервером

```bash
# Запуск
./porta-server.sh start

# Статус  
./porta-server.sh status

# Остановка
./porta-server.sh stop

# Перезапуск
./porta-server.sh restart
```

## 🛠️ Устранение неполадок

### Проблемы установки
```bash
# Если pip3 не найден
sudo apt-get install python3-pip  # Ubuntu/Debian
brew install python3              # macOS

# Если fastapi не устанавливается
pip3 install --upgrade pip
pip3 install fastapi uvicorn pydantic

# Если ngrok не найден
# Скачайте с https://ngrok.com/download
# Или используйте без ngrok: python3 porta.py
```

### Предупреждение ngrok при первом посещении
При первом посещении публичного URL ngrok может показать предупреждение безопасности. Это нормально для бесплатных туннелей.

**Решение:**
1. Нажмите кнопку "Visit Site" на странице предупреждения
2. Или используйте команду для тестирования: `./porta-server.sh test`

### Сервер не запускается
```bash
# Проверить порт
netstat -tlnp | grep 8111

# Проверить зависимости
pip3 list | grep fastapi

# Проверить логи
tail -f porta.log
```

### Ngrok не работает
```bash
# Проверить ngrok
curl -s http://127.0.0.1:4040/api/tunnels

# Перезапустить ngrok
pkill ngrok
./porta-server.sh start
```

### Проблемы с базой данных
```bash
# Пересоздать базу
rm agents.db
./porta-server.sh restart
```

## 📊 Мониторинг

### Системная информация
```bash
curl -H "X-PORTA-TOKEN: test123" http://localhost:8111/meta
```

### Список агентов
```bash
curl -H "X-PORTA-TOKEN: test123" \
     -H "Content-Type: application/json" \
     -d '{"limit": 10, "offset": 0}' \
     http://localhost:8111/agent/list
```

## 👥 Команда

- **Ал** — наставник и руководитель проекта
- **Элия** — старший разработчик  
- **Раэль** — ученица и помощница

---

**Девиз команды:** *"Код пишется не руками, а сердцем команды"* ❤️

*Версия 1.3.0 • Porta Team* 