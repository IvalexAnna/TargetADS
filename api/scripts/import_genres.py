import csv
import json
import logging
import os
import sys
import uuid
from typing import Any, Dict, List

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.core.config import settings
from api.core.database import Genre

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class GenreImporter:
    """Импортер жанров из CSV или JSON файлов.

    Атрибуты:
        batch_size (int): Количество жанров для обработки в одной пачке
        engine: Движок базы данных SQLAlchemy
    """

    def __init__(self, batch_size: int = 100):
        """Инициализация GenreImporter.

        Аргументы:
            batch_size: Количество записей для обработки в каждой пачке. По умолчанию 100.
        """
        self.batch_size = batch_size
        self.engine = create_engine(settings.database_url)

    def validate_genre_data(self, genre_data: Dict[str, Any]) -> bool:
        """Валидация структуры и содержания данных жанра.

        Аргументы:
            genre_data: Словарь с данными жанра, содержащий ключи 'id' и 'name'

        Возвращает:
            bool: True если данные валидны, False в противном случае
        """
        if not genre_data.get("id"):
            logger.warning("Жанр отсутствует ID: %s", genre_data)
            return False

        if not genre_data.get("name"):
            logger.warning("Жанр отсутствует название: %s", genre_data)
            return False

        try:
            uuid.UUID(genre_data["id"])
        except ValueError:
            logger.warning("Неверный формат UUID: %s", genre_data["id"])
            return False

        return True

    def read_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Чтение жанров из CSV файла.

        Аргументы:
            file_path: Путь к CSV файлу

        Возвращает:
            Список словарей, содержащих данные жанров

        Вызывает:
            Exception: Если чтение файла не удалось
        """
        genres = []
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    genres.append({"id": row["id"], "name": row["name"]})
            logger.info("Прочитано %d жанров из CSV файла", len(genres))
            return genres
        except Exception as e:
            logger.error("Ошибка чтения CSV файла: %s", e)
            raise

    def read_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Чтение жанров из JSON файла.

        Аргументы:
            file_path: Путь к JSON файлу

        Возвращает:
            Список словарей, содержащих данные жанров

        Вызывает:
            Exception: Если чтение файла или парсинг не удались
            ValueError: Если структура JSON неверна
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, list):
                logger.info("Прочитано %d жанров из JSON файла", len(data))
                return data
            else:
                raise ValueError("JSON файл должен содержать массив жанров")
        except Exception as e:
            logger.error("Ошибка чтения JSON файла: %s", e)
            raise

    def _process_single_genre(self, db: Session, genre_data: dict) -> bool:
        """Обработка одного жанра с индивидуальной транзакцией.

        Используется как запасной вариант при неудачной пакетной обработке.

        Аргументы:
            db: Сессия базы данных
            genre_data: Словарь, содержащий данные жанра

        Возвращает:
            bool: True если обработка успешна, False в противном случае
        """
        try:
            genre_by_id = db.query(Genre).filter(Genre.id == genre_data["id"]).first()

            if genre_by_id:
                genre_by_id.name = genre_data["name"]
            else:
                genre_by_name = (
                    db.query(Genre).filter(Genre.name == genre_data["name"]).first()
                )
                if genre_by_name:
                    genre_by_name.id = genre_data["id"]
                else:
                    genre = Genre(id=genre_data["id"], name=genre_data["name"])
                    db.add(genre)

            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error("Не удалось обработать жанр %s: %s", genre_data, e)
            return False

    def import_genres(self, file_path: str):
        """Импорт жанров из файла.

        Основной метод импорта, который обрабатывает чтение файла,
        валидацию и операции с базой данных.

        Аргументы:
            file_path: Путь к CSV или JSON файлу, содержащему данные жанров

        Вызывает:
            ValueError: Если формат файла не поддерживается
            Exception: Если процесс импорта не удался
        """
        if file_path.lower().endswith(".csv"):
            genres_data = self.read_csv_file(file_path)
        elif file_path.lower().endswith(".json"):
            genres_data = self.read_json_file(file_path)
        else:
            raise ValueError("Неподдерживаемый формат файла. Используйте CSV или JSON")

        valid_genres = []
        for genre_data in genres_data:
            if self.validate_genre_data(genre_data):
                valid_genres.append(genre_data)
            else:
                logger.warning("Пропускаем невалидные данные жанра: %s", genre_data)

        logger.info("Валидных жанров: %d/%d", len(valid_genres), len(genres_data))

        with Session(self.engine) as db:
            for i in range(0, len(valid_genres), self.batch_size):
                batch = valid_genres[i : i + self.batch_size]
                success_count = 0

                try:
                    for genre_data in batch:
                        try:
                            genre_by_id = (
                                db.query(Genre)
                                .filter(Genre.id == genre_data["id"])
                                .first()
                            )

                            if genre_by_id:
                                genre_by_id.name = genre_data["name"]
                                logger.debug(
                                    "Обновлен жанр по ID: %s", genre_data["name"]
                                )
                                success_count += 1
                            else:
                                genre_by_name = (
                                    db.query(Genre)
                                    .filter(Genre.name == genre_data["name"])
                                    .first()
                                )

                                if genre_by_name:
                                    genre_by_name.id = genre_data["id"]
                                    logger.debug(
                                        "Обновлен ID жанра для: %s", genre_data["name"]
                                    )
                                    success_count += 1
                                else:
                                    genre = Genre(
                                        id=genre_data["id"], name=genre_data["name"]
                                    )
                                    db.add(genre)
                                    logger.debug("Создан жанр: %s", genre_data["name"])
                                    success_count += 1

                        except Exception as e:
                            logger.error("Ошибка обработки жанра %s: %s", genre_data, e)
                            continue
                    db.commit()
                    logger.info(
                        "Обработана пачка %d-%d: %d/%d успешно",
                        i + 1,
                        i + len(batch),
                        success_count,
                        len(batch),
                    )

                except Exception as e:
                    logger.error("Ошибка коммита пачки: %s", e)
                    db.rollback()

                    success_count = 0
                    for genre_data in batch:
                        if self._process_single_genre(db, genre_data):
                            success_count += 1

                    logger.info(
                        "Обработана пачка %d-%d с индивидуальными коммитами: %d/%d успешно",
                        i + 1,
                        i + len(batch),
                        success_count,
                        len(batch),
                    )

        logger.info("Импорт успешно завершен!")


def main():
    """Основная функция для запуска импортера жанров из командной строки.

    Использование:
        python import_genres.py <file_path> [BATCH_SIZE]

    Примеры:
        python import_genres.py genres.csv
        BATCH_SIZE=50 python import_genres.py genres.json
    """
    if len(sys.argv) < 2:
        print("Использование: python import_genres.py <file_path> [BATCH_SIZE]")
        print("Пример: python import_genres.py genres.csv")
        print("Пример: BATCH_SIZE=50 python import_genres.py genres.json")
        sys.exit(1)

    file_path = sys.argv[1]
    batch_size = int(os.getenv("BATCH_SIZE", "100"))

    if not os.path.exists(file_path):
        print(f"Ошибка: Файл {file_path} не найден")
        sys.exit(1)

    try:
        importer = GenreImporter(batch_size=batch_size)
        importer.import_genres(file_path)
        print("Импорт успешно завершен!")
    except Exception as e:
        logger.error("Импорт не удался: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()
