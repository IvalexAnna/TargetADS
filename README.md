text
# 📚 Book Database API

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13+-blue?logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red)
![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=docker)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-purple)

[translate:REST API для управления книгами, жанрами и участниками (авторы, редакторы, иллюстраторы) с полной CRUD функциональностью, фильтрацией и пагинацией.]

---

## 🏗 Архитектура

book-api/
├── api/
│ ├── core/ # Конфигурация и подключение к БД
│ ├── endpoints/ # Роутеры API
│ └── schemas/ # Pydantic модели
├── scripts/
│ ├── import_genres.py # Импорт жанров
│ └── seed_data.py # Тестовые данные
├── tests/ # Тесты (pytest)
├── main.py # Точка входа FastAPI
└── docker-compose.yml # Docker конфигурация

text

---

## 🚀 Быстрый старт

### Запуск через Docker Compose (рекомендуется)

Клонируйте репозиторий
git clone git@github.com:IvalexAnna/TargetADS.git
cd book-api

Запустите приложение
docker-compose up --build -d

Приложение будет доступно по http://localhost:8000
Документация API: http://localhost:8000/docs
text

### Локальный запуск

Установите зависимости
uv sync

Настройте переменные окружения (создайте .env файл)
cp .env.example .env

Запустите приложение
uvicorn main:app --reload --host 0.0.0.0 --port 8000

text

---

## ⚙️ Конфигурация

Создайте файл `.env` в корне проекта со следующим содержимым:

POSTGRES_DB=book_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

text

---

## 📡 API Endpoints

### 📖 Книги

#### Получить книги с фильтрацией и пагинацией

curl -X GET "http://localhost:8000/api/v1/books?page=1&page_size=10&sort=rating&order=desc&q=ring"

text

Ответ:

{
"items": [
{
"id": "uuid",
"title": "The Lord of the Rings",
"rating": 9.5,
"description": "Epic fantasy novel",
"published_year": 1954,
"genres": [{"id": "uuid", "name": "Fantasy"}],
"contributors": [{"id": "uuid", "full_name": "J.R.R. Tolkien", "role": "author"}],
"created_at": "2024-01-01T00:00:00Z",
"updated_at": "2024-01-01T00:00:00Z"
}
],
"total": 1,
"page": 1,
"page_size": 10
}

text

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

text

#### Обновить книгу

curl -X PUT "http://localhost:8000/api/v1/books/<book_id>"
-H "Content-Type: application/json"
-d '{"title": "Updated Book Title", "rating": 9.0}'

text

#### Удалить книгу

curl -X DELETE "http://localhost:8000/api/v1/books/<book_id>"

text

---

### 🎭 Жанры

#### Получить все жанры

curl -X GET "http://localhost:8000/api/v1/genres"

text

#### Создать жанр

curl -X POST "http://localhost:8000/api/v1/genres"
-H "Content-Type: application/json"
-d '{"name": "Fantasy"}'

text

---

### 👥 Участники

#### Получить всех участников

curl -X GET "http://localhost:8000/api/v1/contributors"

text

#### Создать участника

curl -X POST "http://localhost:8000/api/v1/contributors"
-H "Content-Type: application/json"
-d '{"full_name": "J.K. Rowling"}'

text

---

### 🩺 Health Check

curl -X GET "http://localhost:8000/api/ping"

text

Ответ:

{"status": "ok"}

text

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
docker-compose exec api python scripts/import_genres.py genres.csv

Импорт из JSON с другим размером батча
BATCH_SIZE=50 python scripts/import_genres.py genres.json

text

### Заполнение тестовыми данными

docker-compose exec api python scripts/seed_data.py

text

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

- Тесты — pytest для всех endpoint'ов и функций  
- Аутентификация — JWT tokens для защиты API  
- Кэширование — Redis для часто запрашиваемых данных  
- Поиск — полнотекстовый поиск по книгам  
- Документация — OpenAPI с примерами для всех параметров  
- Мониторинг — Prometheus метрики и логирование  
- Миграции — Alembic для управления изменениями схемы  
- Фоновая обработка — Celery для тяжелых операций (импорт)  

---

## 👩‍💻 Автор

**Анна Иванова**

[translate:Разработано в рамках тестового задания для TargetADS.] 🚀

| Платформа | Ссылка                                  | Иконка |
|-----------|----------------------------------------|--------|
| **Email**   | [ivalex.anna@gmail.com](mailto:ivalex.anna@gmail.com)     | 📧     |
| **Telegram**| [@IvalexAnna](https://t.me/IvalexAnna)                   | 📱     |
| **GitHub**  | [IvalexAnna](https://github.com/IvalexAnna)              | 🐙     |

[![Email](https://img.shields.io/badge/Email-ivalex.anna@gmail.com-red?logo=gmail)](mailto:ivalex.anna@gmail.com)
[![Telegram](https://img.shields.io/badge/Telegram-@IvalexAnna-blue?logo=telegram)](https://t.me/IvalexAnna)
[![GitHub](https://img.shields.io/badge/GitHub-IvalexAnna-black?logo=github)](https://github.com/IvalexAnna)