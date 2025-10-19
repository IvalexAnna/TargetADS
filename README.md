# 📚 Book Database API

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue?logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red)
![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=docker)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-purple)

REST API для управления книгами, жанрами и участниками (авторы, редакторы, иллюстраторы) с полной CRUD функциональностью, фильтрацией и пагинацией.

---

## 🏗 Архитектура

```
TargetADS/
├── api/
│ ├── core/         # Конфигурация и подключение к БД
│ ├── endpoints/    # Роутеры API
│ ├── schemas/      # Pydantic модели
│ └── scripts/      # Импорт жанров и тестовые данные
├── tests/          # Тесты (pytest)
├── main.py         # Точка входа FastAPI
├── docker-compose.yml # Docker конфигурация
├── Dockerfile      # Dockerfile для API
├── pyproject.toml  # Зависимости проекта
└── .env.example    # Пример файла переменных окружения

```
---

## 🚀 Быстрый старт

### Запуск через Docker Compose (рекомендуется)

Клонируйте репозиторий
```bash
git clone git@github.com:IvalexAnna/TargetADS.git
```
Перейдите в корневую директорию проекта

```bash
cd TargetADS
```

Скопируйте переменные окружения
```bash
cp .env.example .env
```
Запустите приложение
```bash
docker-compose up --build -d
```
```bash
Приложение: http://localhost:8000
Документация: http://localhost:8000/docs
PostgreSQL: localhost:5433
```
### Локальный запуск
Установите uv
```bash
pip install uv
```
Альтернативный вариант:

На Windows через PowerShell:
```bash
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```
На macOS и Linux через curl:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Установка Python 3.12 (Если есть необходимость)
```bash
uv python install 3.12
```
Создайте виртуальное окружение 
```bash
uv venv --python 3.12
```
Установите зависимости
На Linux/macOS:
```bash
source .venv/bin/activate
```
На Windows PowerShell:
```bash
.venv\Scripts\activate
```
Чтобы синхронизировать зависимости из pyproject.toml:
```bash
uv sync
```
Настройте переменные окружения
```bash
cp .env.example .env
(для локального запуска укажите POSTGRES_HOST=localhost и POSTGRES_PORT=5433)
```
Опционально запустите БД
```bash
docker-compose up -d db
```

Запустите приложение
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
---

## ⚙️ Конфигурация

Файл `.env` в корне проекта. Образец — `.env.example`.
```bash
Для Docker Compose (в контейнере API):

POSTGRES_DB=book_db
POSTGRES_USER=change_me
POSTGRES_PASSWORD=password
POSTGRES_HOST=db
POSTGRES_PORT=5432

Для локального запуска (внешний доступ к БД):

POSTGRES_DB=book_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=change_me
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
```
Переменная `PYTHONPATH` настраивается в Compose и Dockerfile.

---

## 📡 API Endpoints

### 📖 Книги

#### Получить книги с фильтрацией и пагинацией
```bash
curl -X GET "http://localhost:8000/api/v1/books?page=1&page_size=10&sort=rating&order=desc&q=ring"

Ответ:

[
{
"id": "uuid",
"title": "The Lord of the Rings",
"rating": 9.5,
"description": "Epic fantasy novel",
"published_year": 1954
}
]
```
#### Создать книгу
```bash
curl -X POST "http://localhost:8000/api/v1/books"
-H "Content-Type: application/json"
-d '{
"title": "New Book",
"rating": 8.3,
"description": "Some description",
"published_year": 2021,
"genre_ids": ["550e8400-e29b-41d4-a716-446655440000"],
"contributors": [
{"contributor_id": "uuid-person", "role": "author"}
]
}'

```
#### Обновить книгу
```bash
curl -X PUT "http://localhost:8000/api/v1/books/<book_id>"
-H "Content-Type: application/json"
-d '{"title": "Updated Book Title", "rating": 9.0}'

}
```

#### Удалить книгу
```bash
curl -X DELETE "http://localhost:8000/api/v1/books/<book_id>"
```

---

### 🎭 Жанры

#### Получить все жанры
```bash
curl -X GET "http://localhost:8000/api/v1/genres"
```

#### Создать жанр
```bash
curl -X POST "http://localhost:8000/api/v1/genres"
-H "Content-Type: application/json"
-d '{"name": "Fantasy"}'
```

---

### 👥 Участники

#### Получить всех участников
```bash
curl -X GET "http://localhost:8000/api/v1/contributors"
``` 

#### Создать участника
```bash
curl -X POST "http://localhost:8000/api/v1/contributors"
-H "Content-Type: application/json"
-d '{"full_name": "J.K. Rowling"}'
```

---

### 🩺 Health Check
```bash
curl -X GET "http://localhost:8000/api/ping"

Ответ:

{"status": "ok"}
```

---

## 🗄 Структура базы данных

| Таблица           | Описание                                          |
|-------------------|--------------------------------------------------|
| `book`            | книги (id, title, rating, description, published_year) |
| `genre`           | жанры (id, name)                                 |
| `contributor`     | участники (id, full_name)                         |
| `book_genre`      | связи книг и жанров                               |
| `book_contributor`| связи книг и участников с ролями                  |

---

### Ограничения

- ✅ Все PK - UUID  
- ✅ Рейтинг: 0.0-10.0 (DECIMAL(3,1))  
- ✅ Год публикации: 1450-2100  
- ✅ Внешние ключи с ON DELETE CASCADE  
- ✅ ENUM ролей: author, editor, illustrator  
- ✅ Аудитные поля created_at/updated_at  

---

## 🛠 Утилиты

### Импорт жанров

## Импорт из CSV
```bash
docker-compose exec api python api/scripts/import_genres.py genres.csv
```

## Импорт из JSON с другим размером батча
```bash
BATCH_SIZE=50 docker-compose exec api python api/scripts/import_genres.py genres.json
```

### Заполнение тестовыми данными

```bash
docker-compose exec api python api/scripts/seed_data.py
```

## 🧪 Тесты

- Локально: `pytest -q`
- В контейнере: `docker-compose exec api pytest -q`
- Основные тесты: `first_task/test_first_task.py`, `tests/tests_second_task.py`

---

## ✅ Выполненные задания

### Обязательные

- Задание 1: Исправление функций Python (пропущено для фокуса на основном API)  
- Задание 2: DDL схема PostgreSQL с ограничениями  
- Задание 3: API книг с фильтрацией, сортировкой, пагинацией + health-check  

### Бонусные

- Задание 4: Полный CRUD для книг с контрибьюторами и жанрами  
- Задание 5: Импорт жанров из CSV/JSON с пачками и идемпотентностью  

---

## 🎯 Особенности реализации

- Фильтрация: по названию, жанру, году, рейтингу  
- Сортировка: по title/rating/published_year (asc/desc)  
- Пагинация: page (≥1), page_size (1-100)  
- Валидация: Pydantic v2 с кастомными валидаторами  
- Идемпотентность: upsert операции при импорте  
- Транзакционность: атомарные операции с БД  

---

## ⏱ Время разработки

Общее время: ~15-18 часов

Распределение:

| Задача                          | Время     |
|--------------------------------|-----------|
| Настройка проекта и DDL         | 2 часа   |
| Базовая CRUD логика             | ~3 часа  |
| Фильтрация и пагинация          | 3 часа   |
| Контрибьюторы и связи           | ~4 часа  |
| Импорт жанров                   | 2 часа   |
| Тестирование и отладка          | ~3 часа  |

---

## 🚧 Что можно улучшить

При большем дедлайне я бы добавила:
С точки зрения проекта:
- Добавить систему аутетификации и регистрации пользователей
- Возможность добавлять книги в "прочитанное" или "желаемое"
- Добавить графики для отображения прочитанных книг и жанров для отслеживания скорости чтения и смены предпочтений
- Добавить возможность оставлять отзывы на книги
- Добавить систему рекомендаций на основе прочитанных книг и предпочтений пользователя
- Добавить систему "Достижений" для отслеживания достижений пользователей (например, прочитать 10 книг, написать отзыв на 5 книг)

С точки зрения архитектуры:
- Настройка CI/CD — GitHub Actions для автоматизации тестов и деплоя  
- Автоматизация проверки кода с помощью линтеров и форматтеров (flake8, mypy, black)
- Тесты — pytest для всех endpoint'ов и функций
- Аутентификация — JWT tokens для защиты API 
- Настройка Alembic для версионирования схемы БД, безопасных миграций без потери данных и возможности отката изменений
- Настройка административной панели — FastAPI-Admin для управления данными 
---

## 👩‍💻 Автор

**Анна Иванова**

Разработано в рамках тестового задания для TargetADS. 🚀


[![Email](https://img.shields.io/badge/Email-ivalex.anna@gmail.com-red?logo=gmail)](mailto:ivalex.anna@gmail.com)
[![Telegram](https://img.shields.io/badge/Telegram-@IvalexAnna-blue?logo=telegram)](https://t.me/IvalexAnna)
[![GitHub](https://img.shields.io/badge/GitHub-IvalexAnna-black?logo=github)](https://github.com/IvalexAnna)