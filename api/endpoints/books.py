"""Book endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_
from typing import List, Optional
import uuid

from api.core.database import get_db, Book, Genre, Contributor, book_genre, book_contributor, RoleEnum
from api.schemas.books import BookCreate, BookResponse, BookUpdate, GenreResponse, GenreCreate, ContributorRole, GenreBase, ContributorResponse

router = APIRouter()


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate, db: Session = Depends(get_db)):
    """Create a new book."""
    print(f"=== DEBUG: Creating book ===")

    # Check if genres exist
    if book_data.genre_ids:
        existing_genres = db.query(Genre).filter(
            Genre.id.in_(book_data.genre_ids)).all()
        if len(existing_genres) != len(book_data.genre_ids):
            missing_ids = set(book_data.genre_ids) - \
                set(g.id for g in existing_genres)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"One or more genre IDs not found: {missing_ids}"
            )

    # Check if contributors exist
    if book_data.contributors:
        contributor_ids = [c.contributor_id for c in book_data.contributors]
        existing_contributors = db.query(Contributor).filter(
            Contributor.id.in_(contributor_ids)).all()
        if len(existing_contributors) != len(contributor_ids):
            missing_ids = set(contributor_ids) - \
                set(c.id for c in existing_contributors)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"One or more contributor IDs not found: {missing_ids}"
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

    db.add(book)
    db.commit()
    db.refresh(book)

    # Add genre associations
    if book_data.genre_ids:
        for genre_id in book_data.genre_ids:
            stmt = book_genre.insert().values(book_id=book_id, genre_id=genre_id)
            db.execute(stmt)

    # Add contributor associations
    if book_data.contributors:
        for contributor_role in book_data.contributors:
            stmt = book_contributor.insert().values(
                book_id=book_id,
                contributor_id=contributor_role.contributor_id,
                role=contributor_role.role
            )
            db.execute(stmt)

    db.commit()

    # Reload book with relationships for response
    book = db.query(Book).options(
        joinedload(Book.genres),
        joinedload(Book.contributors)
    ).filter(Book.id == book_id).first()

    print(f"=== DEBUG: Book created successfully ===")
    return book


@router.get("/books", response_model=dict)
async def get_books(
    q: Optional[str] = Query(None, description="Search in title"),
    genre_id: Optional[uuid.UUID] = Query(None, description="Filter by genre"),
    published_year: Optional[int] = Query(
        None, ge=1450, le=2100, description="Filter by year"),
    rating_min: Optional[float] = Query(
        None, ge=0.0, le=10.0, description="Minimum rating"),
    rating_max: Optional[float] = Query(
        None, ge=0.0, le=10.0, description="Maximum rating"),
    sort: str = Query(
        "title", regex="^(title|rating|published_year)$", description="Sort field"),
    order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Get books with filtering, sorting and pagination."""

    # Базовый запрос с JOIN для жанров
    query = db.query(Book).options(
        joinedload(Book.genres),
        joinedload(Book.contributors)
    )

    # Фильтрация
    if q:
        query = query.filter(Book.title.ilike(f"%{q}%"))

    if genre_id:
        query = query.join(book_genre).filter(
            book_genre.c.genre_id == genre_id)

    if published_year:
        query = query.filter(Book.published_year == published_year)

    if rating_min is not None:
        query = query.filter(Book.rating >= rating_min)

    if rating_max is not None:
        query = query.filter(Book.rating <= rating_max)

    # Сортировка
    sort_column = getattr(Book, sort)
    if order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # Пагинация
    total = query.count()
    offset = (page - 1) * page_size
    books = query.offset(offset).limit(page_size).all()

    # Создаем Pydantic модели
    book_responses = []
    for book in books:
        # Получаем контрибьюторов с ролями
        contributors_with_roles = []
        for contributor in book.contributors:
            # Находим роль для этого контрибьютора и книги
            association = db.query(book_contributor).filter(
                book_contributor.c.book_id == book.id,
                book_contributor.c.contributor_id == contributor.id
            ).first()

            if association:
                contributors_with_roles.append(
                    ContributorResponse(
                        id=contributor.id,
                        full_name=contributor.full_name,
                        role=association.role
                    )
                )

        # Создаем BookResponse
        book_response = BookResponse(
            id=book.id,
            title=book.title,
            rating=float(book.rating) if book.rating else None,
            description=book.description,
            published_year=book.published_year,
            genres=[GenreBase(id=genre.id, name=genre.name)
                    for genre in book.genres],
            contributors=contributors_with_roles,
            created_at=book.created_at,
            updated_at=book.updated_at
        )
        book_responses.append(book_response)

    return {
        "items": book_responses,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, db: Session = Depends(get_db)):
    """Get a specific book by ID."""
    book = db.query(Book).options(
        joinedload(Book.genres),
        joinedload(Book.contributors)
    ).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # Получаем контрибьюторов с ролями
    contributors_with_roles = []
    for contributor in book.contributors:
        association = db.query(book_contributor).filter(
            book_contributor.c.book_id == book.id,
            book_contributor.c.contributor_id == contributor.id
        ).first()

        if association:
            contributors_with_roles.append(
                ContributorResponse(
                    id=contributor.id,
                    full_name=contributor.full_name,
                    role=association.role
                )
            )

    return BookResponse(
        id=book.id,
        title=book.title,
        rating=float(book.rating) if book.rating else None,
        description=book.description,
        published_year=book.published_year,
        genres=[GenreBase(id=genre.id, name=genre.name)
                for genre in book.genres],
        contributors=contributors_with_roles,
        created_at=book.created_at,
        updated_at=book.updated_at
    )


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
        if field not in ['genre_ids', 'contributors']:
            setattr(book, field, value)

    # Update genres if provided
    if 'genre_ids' in update_data:
        # Remove existing genre associations
        db.execute(book_genre.delete().where(book_genre.c.book_id == book_id))

        # Add new genre associations
        for genre_id in update_data['genre_ids']:
            stmt = book_genre.insert().values(book_id=book_id, genre_id=str(genre_id))
            db.execute(stmt)

    # Update contributors if provided
    if 'contributors' in update_data:
        # Remove existing contributor associations
        db.execute(book_contributor.delete().where(
            book_contributor.c.book_id == book_id))

        # Add new contributor associations
        for contributor_role in update_data['contributors']:
            stmt = book_contributor.insert().values(
                book_id=book_id,
                contributor_id=contributor_role['contributor_id'],
                role=contributor_role['role']
            )
            db.execute(stmt)

    db.commit()

    # Reload book with relationships for response
    book = db.query(Book).options(
        joinedload(Book.genres),
        joinedload(Book.contributors)
    ).filter(Book.id == book_id).first()

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
    existing_genre = db.query(Genre).filter(
        Genre.name == genre_data.name).first()
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
