#!/usr/bin/env python3
"""Import genres from CSV or JSON file."""
import uuid
import csv
import json
import logging
from typing import List, Dict, Any
import os
import sys

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Добавляем путь к корню проекта для импортов
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.core.database import Genre
from api.core.config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GenreImporter:
    """Importer for genres from CSV or JSON files."""

    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
        self.engine = create_engine(settings.database_url)

    def validate_genre_data(self, genre_data: Dict[str, Any]) -> bool:
        """Validate genre data."""
        if not genre_data.get('id'):
            logger.warning("Genre missing ID: %s", genre_data)
            return False

        if not genre_data.get('name'):
            logger.warning("Genre missing name: %s", genre_data)
            return False

        try:
            uuid.UUID(genre_data['id'])
        except ValueError:
            logger.warning("Invalid UUID format: %s", genre_data['id'])
            return False

        return True

    def read_csv_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Read genres from CSV file."""
        genres = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    genres.append({
                        'id': row['id'],
                        'name': row['name']
                    })
            logger.info("Read %d genres from CSV file", len(genres))
            return genres
        except Exception as e:
            logger.error("Error reading CSV file: %s", e)
            raise

    def read_json_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Read genres from JSON file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if isinstance(data, list):
                logger.info("Read %d genres from JSON file", len(data))
                return data
            else:
                raise ValueError("JSON file should contain an array of genres")
        except Exception as e:
            logger.error("Error reading JSON file: %s", e)
            raise

    def _process_single_genre(self, db: Session, genre_data: dict):
        """Process a single genre with individual transaction."""
        try:
            genre_by_id = db.query(Genre).filter(Genre.id == genre_data['id']).first()

            if genre_by_id:
                genre_by_id.name = genre_data['name']
            else:
                genre_by_name = db.query(Genre).filter(Genre.name == genre_data['name']).first()
                if genre_by_name:
                    genre_by_name.id = genre_data['id']
                else:
                    genre = Genre(id=genre_data['id'], name=genre_data['name'])
                    db.add(genre)

            db.commit()
            return True
        except Exception as e:
            db.rollback()
            logger.error("Failed to process genre %s: %s", genre_data, e)
            return False

    def import_genres(self, file_path: str):
        """Import genres from file."""
        # Определяем тип файла
        if file_path.lower().endswith('.csv'):
            genres_data = self.read_csv_file(file_path)
        elif file_path.lower().endswith('.json'):
            genres_data = self.read_json_file(file_path)
        else:
            raise ValueError("Unsupported file format. Use CSV or JSON")

        # Валидируем данные
        valid_genres = []
        for genre_data in genres_data:
            if self.validate_genre_data(genre_data):
                valid_genres.append(genre_data)
            else:
                logger.warning("Skipping invalid genre data: %s", genre_data)

        logger.info("Valid genres: %d/%d", len(valid_genres), len(genres_data))

        # Импортируем пачками
        with Session(self.engine) as db:
            for i in range(0, len(valid_genres), self.batch_size):
                batch = valid_genres[i:i + self.batch_size]
                success_count = 0

                try:
                    for genre_data in batch:
                        try:
                            # Сначала проверяем по ID
                            genre_by_id = db.query(Genre).filter(Genre.id == genre_data['id']).first()

                            if genre_by_id:
                                # Обновляем существующий жанр по ID
                                genre_by_id.name = genre_data['name']
                                logger.debug("Updated genre by ID: %s", genre_data['name'])
                                success_count += 1
                            else:
                                # Проверяем по имени ДО создания нового
                                genre_by_name = db.query(Genre).filter(Genre.name == genre_data['name']).first()

                                if genre_by_name:
                                    # Жанр с таким именем уже существует - обновляем его ID
                                    genre_by_name.id = genre_data['id']
                                    logger.debug("Updated genre ID for: %s", genre_data['name'])
                                    success_count += 1
                                else:
                                    # Создаем новый жанр
                                    genre = Genre(
                                        id=genre_data['id'],
                                        name=genre_data['name']
                                    )
                                    db.add(genre)
                                    logger.debug("Created genre: %s", genre_data['name'])
                                    success_count += 1

                        except Exception as e:
                            logger.error("Error processing genre %s: %s", genre_data, e)
                            continue

                    # Коммитим батч
                    db.commit()
                    logger.info("Processed batch %d-%d: %d/%d successful", 
                               i + 1, i + len(batch), success_count, len(batch))

                except Exception as e:
                    logger.error("Error committing batch: %s", e)
                    db.rollback()
                    
                    # Пробуем обработать батч по одному
                    success_count = 0
                    for genre_data in batch:
                        if self._process_single_genre(db, genre_data):
                            success_count += 1
                    
                    logger.info("Processed batch %d-%d with individual commits: %d/%d successful", 
                               i + 1, i + len(batch), success_count, len(batch))

        logger.info("Import completed successfully!")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python import_genres.py <file_path> [BATCH_SIZE]")
        print("Example: python import_genres.py genres.csv")
        print("Example: BATCH_SIZE=50 python import_genres.py genres.json")
        sys.exit(1)

    file_path = sys.argv[1]
    batch_size = int(os.getenv('BATCH_SIZE', '100'))

    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found")
        sys.exit(1)

    try:
        importer = GenreImporter(batch_size=batch_size)
        importer.import_genres(file_path)
        print("✅ Import completed successfully!")
    except Exception as e:
        logger.error("Import failed: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    main()