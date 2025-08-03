# 🧹 СПИСОК ФАЙЛОВ ДЛЯ ОЧИСТКИ ПРОЕКТА PORTA

## 📊 ОБЩАЯ СТАТИСТИКА
- **Всего файлов для удаления:** ~200+
- **Общий размер мусора:** ~53MB (в основном node_modules)
- **Категории:** 5 основных групп

---

## 🗑️ 1. ВРЕМЕННЫЕ ФАЙЛЫ (УДАЛИТЬ)

### Логи и PID файлы:
- `./porta.log` - лог сервера (можно архивировать)
- `./ngrok.log` - лог ngrok (можно архивировать)
- `./porta.pid` - PID файл сервера
- `./ngrok.pid` - PID файл ngrok
- `./ngrok.url` - временный URL файл

### Python кэш:
- `./__pycache__/` - директория Python кэша
- `./__pycache__/porta.cpython-38.pyc` - скомпилированный Python файл

---

## 📦 2. NODE.JS ЗАВИСИМОСТИ (ПЕРЕМЕСТИТЬ В .gitignore)

### Основные node_modules:
- `./mcp/memory_bank_engine/node_modules/` - **53MB** зависимостей
- `./mcp/memory_bank_engine/node_modules/http-errors/node_modules/` - вложенные зависимости

### Рекомендация:
- Добавить `node_modules/` в `.gitignore`
- Использовать `npm install` при необходимости
- Не коммитить зависимости в репозиторий

---

## 🧪 3. ТЕСТОВЫЕ ФАЙЛЫ (УДАЛИТЬ ИЛИ ПЕРЕМЕСТИТЬ)

### Тестовые данные:
- `./agent_test.txt` - тестовый файл агента
- `./test_hello.txt` - тестовый файл
- `./test_read_file.txt` - тестовый файл

### Рекомендация:
- Удалить или переместить в `./tests/` директорию
- Создать структуру тестов

---

## 📚 4. ДОКУМЕНТАЦИЯ (ОРГАНИЗОВАТЬ)

### Файлы в корне:
- `./requirements.txt` - **ОСТАВИТЬ** (важный файл)
- `./readme.md` - **ОСТАВИТЬ** (основная документация)

### Файлы в memory-bank-data:
- `./memory-bank-data/Porta/activeContext.md` - **ОСТАВИТЬ** (важный контекст)
- `./memory-bank-data/Porta/progress.md` - **ОСТАВИТЬ** (прогресс проекта)
- `./memory-bank-data/Porta/techContext.md` - **ОСТАВИТЬ** (технический контекст)
- `./memory-bank-data/Porta/projectbrief.md` - **ОСТАВИТЬ** (описание проекта)
- `./memory-bank-data/Porta/list_dir_implementation.md` - **ОСТАВИТЬ** (документация)
- `./memory-bank-data/Porta/productContext.md` - **ОСТАВИТЬ** (контекст продукта)
- `./memory-bank-data/Porta/network_security_concepts.md` - **ОСТАВИТЬ** (безопасность)
- `./memory-bank-data/Porta/technical_patterns.md` - **ОСТАВИТЬ** (паттерны)
- `./memory-bank-data/Porta/external_access_implementation.md` - **ОСТАВИТЬ** (реализация)
- `./memory-bank-data/Porta/team_growth_dynamics.md` - **ОСТАВИТЬ** (динамика команды)
- `./memory-bank-data/Porta/systemPatterns.md` - **ОСТАВИТЬ** (системные паттерны)

### Файлы в notes:
- `./notes/info.txt` - **ОСТАВИТЬ** (важные заметки)

---

## 🗄️ 5. БАЗЫ ДАННЫХ (ОРГАНИЗОВАТЬ)

### Рабочие БД:
- `./agents.db` - **ОСТАВИТЬ** (рабочая база агентов)
- `./docs/project_clean.db` - **ОСТАВИТЬ** (этот файл)

### Рекомендация:
- Создать директорию `./data/` для баз данных
- Переместить `agents.db` в `./data/agents.db`
- Добавить `*.db` в `.gitignore` (кроме примеров)

---

## 🎯 ПЛАН ОЧИСТКИ

### Этап 1: Быстрая очистка (удалить)
```bash
# Удалить временные файлы
rm -f porta.log ngrok.log porta.pid ngrok.pid ngrok.url
rm -rf __pycache__/

# Удалить тестовые файлы
rm -f agent_test.txt test_hello.txt test_read_file.txt
```

### Этап 2: Организация (переместить)
```bash
# Создать структуру директорий
mkdir -p data/ tests/ logs/

# Переместить базу данных
mv agents.db data/

# Переместить тестовые файлы (если нужны)
mv test_*.txt tests/ 2>/dev/null || true
```

### Этап 3: Gitignore (добавить)
```bash
# Добавить в .gitignore:
echo "node_modules/" >> .gitignore
echo "*.log" >> .gitignore
echo "*.pid" >> .gitignore
echo "*.url" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "data/*.db" >> .gitignore
```

### Этап 4: Node.js зависимости
```bash
# Удалить node_modules (можно восстановить через npm install)
rm -rf mcp/memory_bank_engine/node_modules/
```

---

## 📈 ОЖИДАЕМЫЙ РЕЗУЛЬТАТ

### После очистки:
- **Уменьшение размера репозитория:** ~53MB
- **Чистота корневой директории:** только важные файлы
- **Структурированность:** логичная организация файлов
- **Безопасность:** конфиденциальные данные в .gitignore

### Структура после очистки:
```
Porta/
├── porta.py              # основной сервер
├── porta-server.sh       # скрипт управления
├── readme.md            # документация
├── requirements.txt     # зависимости Python
├── docs/               # документация
├── data/               # базы данных
├── tests/              # тестовые файлы
├── logs/               # логи (если нужны)
├── mcp/                # MCP компоненты
├── memory-bank-data/   # данные банка памяти
└── scripts/            # вспомогательные скрипты
```

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

1. **НЕ УДАЛЯТЬ** файлы из `memory-bank-data/` - это важный контекст проекта
2. **СОХРАНИТЬ** `agents.db` - содержит данные агентов
3. **ДОБАВИТЬ** в `.gitignore` временные файлы
4. **ПРОТЕСТИРОВАТЬ** после очистки - убедиться, что все работает

---

## 🎯 ПРИОРИТЕТЫ ОЧИСТКИ

1. **Высокий приоритет:** Удалить временные файлы и node_modules
2. **Средний приоритет:** Организовать структуру директорий
3. **Низкий приоритет:** Настроить .gitignore

**Общий вывод:** Проект в хорошем состоянии, но нужна небольшая уборка для чистоты и организации.
