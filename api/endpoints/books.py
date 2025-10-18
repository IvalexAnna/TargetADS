"""Book endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from api.core.database import get_db, Book, Genre, book_genre
from api.schemas.books import BookCreate, BookResponse, BookUpdate, GenreResponse, GenreCreate

router = APIRouter()


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate, db: Session = Depends(get_db)):
    """Create a new book."""
    print(f"=== DEBUG: Creating book ===")
    print(f"Book data: {book_data}")
    
    # Check if genres exist
    if book_data.genre_ids:
        print(f"Looking for genres with IDs: {book_data.genre_ids}")
        
        # Get all existing genres for debug
        all_genres = db.query(Genre).all()
        print(f"All genres in DB: {[(str(g.id), g.name) for g in all_genres]}")
        
        existing_genres = db.query(Genre).filter(Genre.id.in_(book_data.genre_ids)).all()
        print(f"Found genres: {[(str(g.id), g.name) for g in existing_genres]}")
        
        if len(existing_genres) != len(book_data.genre_ids):
            missing_ids = set(book_data.genre_ids) - set(g.id for g in existing_genres)
            print(f"Missing genre IDs: {missing_ids}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"One or more genre IDs not found: {missing_ids}"
            )

    # Create book
    book_id = uuid.uuid4()
    book = Book(
        id=book_id,
        title=book_data.title,
        rating=book_data.rating,
        description=book_data.description,
        published_year=book_data.published_year
    )
    
    # Сначала сохраняем книгу в базу
    db.add(book)
    db.commit()  # ✅ ВАЖНО: коммитим книгу сначала
    db.refresh(book)  # ✅ Обновляем объект книги
    
    print(f"Book saved with ID: {book_id}")

    # Теперь добавляем связи с жанрами
    if book_data.genre_ids:
        for genre_id in book_data.genre_ids:
            stmt = book_genre.insert().values(book_id=book_id, genre_id=genre_id)
            db.execute(stmt)
        
        db.commit()  # ✅ Коммитим связи
    
    # Обновляем книгу чтобы получить связи с жанрами
    db.refresh(book)
    
    print(f"=== DEBUG: Book created successfully ===")
    return book


@router.get("/books", response_model=List[BookResponse])
async def get_books(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all books with pagination."""
    books = db.query(Book).offset(skip).limit(limit).all()
    return books


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, db: Session = Depends(get_db)):
    """Get a specific book by ID."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    return book


@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(book_id: str, book_data: BookUpdate, db: Session = Depends(get_db)):
    """Update a book."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # Update fields
    update_data = book_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field != 'genre_ids':
            setattr(book, field, value)

    # Update genres if provided
    if 'genre_ids' in update_data:
        # Remove existing genre associations
        db.execute(book_genre.delete().where(book_genre.c.book_id == book_id))
        
        # Add new genre associations
        for genre_id in update_data['genre_ids']:
            stmt = book_genre.insert().values(book_id=book_id, genre_id=str(genre_id))
            db.execute(stmt)

    db.commit()
    db.refresh(book)
    return book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str, db: Session = Depends(get_db)):
    """Delete a book."""
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    db.delete(book)
    db.commit()


@router.post("/genres", response_model=GenreResponse, status_code=status.HTTP_201_CREATED)
async def create_genre(genre_data: GenreCreate, db: Session = Depends(get_db)):
    """Create a new genre."""
    # Check if genre name already exists
    existing_genre = db.query(Genre).filter(Genre.name == genre_data.name).first()
    if existing_genre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Genre with this name already exists"
        )

    genre = Genre(
        id=str(uuid.uuid4()),
        name=genre_data.name
    )
    
    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


@router.get("/genres", response_model=List[GenreResponse])
async def get_genres(db: Session = Depends(get_db)):
    """Get all genres."""
    genres = db.query(Genre).all()
    return genres