"""Fill database with test data."""
import uuid
import sys
import os

# Добавляем корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.core.database import Book, Genre, Contributor, book_genre, book_contributor, RoleEnum
from api.core.config import settings


def fill_database():
    """Add test books, genres and contributors."""
    print("Adding test data to database...")

    engine = create_engine(settings.database_url)
    db = Session(engine)

    try:
        # Check if data already exists
        existing_books_count = db.query(Book).count()
        existing_genres_count = db.query(Genre).count()
        existing_contributors_count = db.query(Contributor).count()
        
        if existing_books_count > 0 or existing_genres_count > 0 or existing_contributors_count > 0:
            print("Database already contains data. Skipping seed operation.")
            return

        # Create genres
        horror = Genre(id=uuid.uuid4(), name="Horror")
        adventure = Genre(id=uuid.uuid4(), name="Adventure")
        thriller = Genre(id=uuid.uuid4(), name="Thriller")
        historical = Genre(id=uuid.uuid4(), name="Historical Fiction")

        db.add_all([horror, adventure, thriller, historical])
        db.commit()

        # Create contributors
        king = Contributor(id=uuid.uuid4(), full_name="Stephen King")
        crouch = Contributor(id=uuid.uuid4(), full_name="Blake Crouch")
        brown = Contributor(id=uuid.uuid4(), full_name="Dan Brown")

        db.add_all([king, crouch, brown])
        db.commit()

        # Create books
        books = [
            Book(
                id=uuid.uuid4(),
                title="The Shining",
                rating=8.7,
                description="Horror story about a haunted hotel",
                published_year=1977
            ),
            Book(
                id=uuid.uuid4(),
                title="Recursion",
                rating=8.9,
                description="Mind-bending thriller about memory and reality",
                published_year=2019
            ),
            Book(
                id=uuid.uuid4(),
                title="The Da Vinci Code",
                rating=7.9,
                description="Fast-paced adventure involving secret societies",
                published_year=2003
            ),
            Book(
                id=uuid.uuid4(),
                title="The Terror",
                rating=8.1,
                description="Historical fiction about a doomed Arctic expedition",
                published_year=2007
            )
        ]

        db.add_all(books)
        db.commit()

        # Connect books with genres
        db.execute(book_genre.insert().values(
            book_id=books[0].id, genre_id=horror.id))
        db.execute(book_genre.insert().values(
            book_id=books[1].id, genre_id=thriller.id))
        db.execute(book_genre.insert().values(
            book_id=books[2].id, genre_id=adventure.id))
        db.execute(book_genre.insert().values(
            book_id=books[3].id, genre_id=historical.id))

        # Connect books with contributors
        db.execute(book_contributor.insert().values(
            book_id=books[0].id, contributor_id=king.id, role=RoleEnum.author
        ))
        db.execute(book_contributor.insert().values(
            book_id=books[1].id, contributor_id=crouch.id, role=RoleEnum.author
        ))
        db.execute(book_contributor.insert().values(
            book_id=books[2].id, contributor_id=brown.id, role=RoleEnum.author
        ))
        db.execute(book_contributor.insert().values(
            book_id=books[3].id, contributor_id=crouch.id, role=RoleEnum.author
        ))

        db.commit()
        print("Test data added successfully!")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    fill_database()