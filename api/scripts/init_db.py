import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from api.core.database import Base, engine


def init_database():
    """Создает все таблицы в базе данных на основе моделей SQLAlchemy.

    Функция использует метаданные из Base для создания таблиц,
    определенных в моделях приложения. Выполняется при первом запуске
    или при необходимости пересоздания структуры БД.

    Raises:
        Exception: Если произошла ошибка при создании таблиц
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")


if __name__ == "__main__":
    init_database()
