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
├── Dockerfile
├── pyproject.toml
└── .env.example

```


## 🚀 Быстрый старт

### Запуск через Docker Compose (рекомендуется)

Клонируйте репозиторий
git clone git@github.com:IvalexAnna/TargetADS.git
cd TargetADS

Скопируйте переменные окружения
cp .env.example .env

Запустите приложение
docker-compose up --build -d

Приложение: http://localhost:8000
Документация: http://localhost:8000/docs
PostgreSQL: localhost:5433 (внешний порт)

### Локальный запуск

Создайте виртуальное окружение и установите зависимости
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
или
pip install fastapi uvicorn[standard] sqlalchemy psycopg2-binary pydantic pydantic-settings

Настройте переменные окружения
cp .env.example .env
(для локального запуска укажите POSTGRES_HOST=localhost и POSTGRES_PORT=5433)

Опционально запустите БД
docker-compose up -d db

Запустите приложение
uvicorn main:app --reload --host 0.0.0.0 --port 8000

---

## ⚙️ Конфигурация

Файл `.env` в корне проекта. Образец — `.env.example`.

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

Переменная `PYTHONPATH` настраивается в Compose и Dockerfile.

---

## 📡 API Endpoints

### 📖 Книги

#### Получить книги с фильтрацией и пагинацией

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

#### Создать книгу

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


#### Обновить книгу

curl -X PUT "http://localhost:8000/api/v1/books/<book_id>"
-H "Content-Type: application/json"
-d '{"title": "Updated Book Title", "rating": 9.0}'

}

#### Удалить книгу

curl -X DELETE "http://localhost:8000/api/v1/books/<book_id>"

---

### 🎭 Жанры

#### Получить все жанры

curl -X GET "http://localhost:8000/api/v1/genres"

#### Создать жанр

curl -X POST "http://localhost:8000/api/v1/genres"
-H "Content-Type: application/json"
-d '{"name": "Fantasy"}'

---

### 👥 Участники

#### Получить всех участников

curl -X GET "http://localhost:8000/api/v1/contributors"

#### Создать участника

curl -X POST "http://localhost:8000/api/v1/contributors"
-H "Content-Type: application/json"
-d '{"full_name": "J.K. Rowling"}'

---

### 🩺 Health Check

curl -X GET "http://localhost:8000/api/ping"

Ответ:

{"status": "ok"}

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

Импорт из CSV
docker-compose exec api python api/scripts/import_genres.py genres.csv

Импорт из JSON с другим размером батча
BATCH_SIZE=50 docker-compose exec api python api/scripts/import_genres.py genres.json

### Заполнение тестовыми данными

docker-compose exec api python api/scripts/seed_data.py

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
| Настройка проекта и DDL         | 2 часа    |
| Базовая CRUD логика             | 3 часа    |
| Фильтрация и пагинация          | 3 часа    |
| Контрибьюторы и связи           | 4 часа    |
| Импорт жанров                  | 2 часа    |
| Тестирование и отладка          | 1.5 часа  |

---

## 🚧 Что можно улучшить

При большем дедлайне я бы добавила:
С точки зрения проекта:
- Настройка административной панели — FastAPI-Admin для управления данными
- Аутентификация — JWT tokens для защиты API  
- 
- Поиск — полнотекстовый поиск по книгам  

С точки зрения архитектуры:
- Настройка CI/CD — GitHub Actions для автоматизации тестов и деплоя  
- Тесты — pytest для всех endpoint'ов и функций
- Миграции — Alembic для управления изменениями схемы  
- Фоновая обработка — Celery для тяжелых операций (импорт)

Документация — OpenAPI с примерами для всех параметров  
Мониторинг — Prometheus метрики и логирование 
---

## 👩‍💻 Автор

**Анна Иванова**

Разработано в рамках тестового задания для TargetADS. 🚀


[![Email](https://img.shields.io/badge/Email-ivalex.anna@gmail.com-red?logo=gmail)](mailto:ivalex.anna@gmail.com)
[![Telegram](https://img.shields.io/badge/Telegram-@IvalexAnna-blue?logo=telegram)](https://t.me/IvalexAnna)
[![GitHub](https://img.shields.io/badge/GitHub-IvalexAnna-black?logo=github)](https://github.com/IvalexAnna)