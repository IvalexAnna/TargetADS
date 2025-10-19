import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, joinedload

from api.core.database import (Book, Contributor, Genre, RoleEnum,
                               book_contributor, book_genre, get_db)
from api.schemas.books import (BookCreate, BookResponse, BookUpdate,
                               ContributorResponse, ContributorRole, GenreBase,
                               GenreCreate, GenreResponse)

router = APIRouter()


@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(book_data: BookCreate, db: Session = Depends(get_db)):
    """Создает новую книгу.

    Args:
        book_data: Данные для создания книги.
        db: Сессия базы данных.

    Returns:
        BookResponse: Созданная книга.

    Raises:
        HTTPException: 400 - если книга с таким названием уже существует или указаны несуществующие жанры/контрибьюторы.
    """
    existing_book = (
        db.query(Book)
        .filter(func.lower(Book.title) == func.lower(book_data.title))
        .first()
    )
    if existing_book:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book with this title already exists",
        )

    if book_data.genre_ids:
        existing_genres = (
            db.query(Genre).filter(Genre.id.in_(book_data.genre_ids)).all()
        )
        if len(existing_genres) != len(book_data.genre_ids):
            missing_ids = set(book_data.genre_ids) - set(g.id for g in existing_genres)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"One or more genre IDs not found: {missing_ids}",
            )

    if book_data.contributors:
        contributor_ids = [c.contributor_id for c in book_data.contributors]
        existing_contributors = (
            db.query(Contributor).filter(Contributor.id.in_(contributor_ids)).all()
        )
        if len(existing_contributors) != len(contributor_ids):
            missing_ids = set(contributor_ids) - set(
                c.id for c in existing_contributors
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"One or more contributor IDs not found: {missing_ids}",
            )

    book_id = str(uuid.uuid4())
    book = Book(
        id=book_id,
        title=book_data.title,
        rating=book_data.rating,
        description=book_data.description,
        published_year=book_data.published_year,
    )

    db.add(book)
    db.flush()

    if book_data.genre_ids:
        for genre_id in book_data.genre_ids:
            stmt = book_genre.insert().values(book_id=book_id, genre_id=str(genre_id))
            db.execute(stmt)

    if book_data.contributors:
        for contributor_role in book_data.contributors:
            stmt = book_contributor.insert().values(
                book_id=book_id,
                contributor_id=str(contributor_role.contributor_id),
                role=contributor_role.role.value,
            )
            db.execute(stmt)

    db.commit()

    book = (
        db.query(Book)
        .options(joinedload(Book.genres))
        .filter(Book.id == book_id)
        .first()
    )

    contributors_with_roles = []
    if book_data.contributors:
        for contributor_role in book_data.contributors:
            contributor = (
                db.query(Contributor)
                .filter(Contributor.id == contributor_role.contributor_id)
                .first()
            )

            if contributor:
                contributors_with_roles.append(
                    ContributorResponse(
                        id=contributor.id,
                        full_name=contributor.full_name,
                        role=contributor_role.role,
                    )
                )

    return BookResponse(
        id=book.id,
        title=book.title,
        rating=float(book.rating) if book.rating else None,
        description=book.description,
        published_year=book.published_year,
        genres=[GenreBase(id=genre.id, name=genre.name) for genre in book.genres],
        contributors=contributors_with_roles,
        created_at=book.created_at,
        updated_at=book.updated_at,
    )


@router.get("/books", response_model=dict)
async def get_books(
    q: Optional[str] = Query(None, description="Поиск по названию и описанию"),
    genre_id: Optional[uuid.UUID] = Query(None, description="Фильтр по жанру"),
    genre_ids: Optional[List[uuid.UUID]] = Query(
        None, description="Фильтр по нескольким жанрам"
    ),
    contributor_id: Optional[uuid.UUID] = Query(
        None, description="Фильтр по контрибьютору"
    ),
    published_year: Optional[int] = Query(
        None, ge=1450, le=2100, description="Фильтр по году"
    ),
    published_year_min: Optional[int] = Query(
        None, ge=1450, le=2100, description="Минимальный год публикации"
    ),
    published_year_max: Optional[int] = Query(
        None, ge=1450, le=2100, description="Максимальный год публикации"
    ),
    rating_min: Optional[float] = Query(
        None, ge=0.0, le=10.0, description="Минимальный рейтинг"
    ),
    rating_max: Optional[float] = Query(
        None, ge=0.0, le=10.0, description="Максимальный рейтинг"
    ),
    sort: str = Query(
        "title",
        pattern="^(title|rating|published_year|created_at)$",
        description="Поле сортировки",
    ),
    order: str = Query("asc", pattern="^(asc|desc)$", description="Порядок сортировки"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
    db: Session = Depends(get_db),
):
    """Получает список книг с фильтрацией, сортировкой и пагинацией.

    Args:
        q: Поисковый запрос по названию и описанию.
        genre_id: ID жанра для фильтрации.
        genre_ids: Список ID жанров для фильтрации.
        contributor_id: ID контрибьютора для фильтрации.
        published_year: Год публикации для точной фильтрации.
        published_year_min: Минимальный год публикации.
        published_year_max: Максимальный год публикации.
        rating_min: Минимальный рейтинг.
        rating_max: Максимальный рейтинг.
        sort: Поле для сортировки.
        order: Порядок сортировки.
        page: Номер страницы.
        page_size: Размер страницы.
        db: Сессия базы данных.

    Returns:
        dict: Словарь с книгами и метаданными пагинации.
    """
    query = db.query(Book).options(
        joinedload(Book.genres), joinedload(Book.contributors)
    )

    if q:
        query = query.filter(
            or_(Book.title.ilike(f"%{q}%"), Book.description.ilike(f"%{q}%"))
        )

    if genre_id:
        query = query.join(book_genre).filter(book_genre.c.genre_id == genre_id)

    if genre_ids:
        query = (
            query.join(book_genre)
            .filter(book_genre.c.genre_id.in_(genre_ids))
            .group_by(Book.id)
            .having(func.count(book_genre.c.genre_id) == len(genre_ids))
        )

    if contributor_id:
        query = query.join(book_contributor).filter(
            book_contributor.c.contributor_id == contributor_id
        )

    if published_year:
        query = query.filter(Book.published_year == published_year)

    if published_year_min is not None:
        query = query.filter(Book.published_year >= published_year_min)

    if published_year_max is not None:
        query = query.filter(Book.published_year <= published_year_max)

    if rating_min is not None:
        query = query.filter(Book.rating >= rating_min)

    if rating_max is not None:
        query = query.filter(Book.rating <= rating_max)

    sort_column = getattr(Book, sort)
    if order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    total = query.count()
    offset = (page - 1) * page_size
    books = query.offset(offset).limit(page_size).all()

    book_responses = []
    for book in books:
        contributors_with_roles = []
        for contributor in book.contributors:
            association = (
                db.query(book_contributor)
                .filter(
                    book_contributor.c.book_id == book.id,
                    book_contributor.c.contributor_id == contributor.id,
                )
                .first()
            )

            if association:
                contributors_with_roles.append(
                    ContributorResponse(
                        id=contributor.id,
                        full_name=contributor.full_name,
                        role=association.role,
                    )
                )

        book_response = BookResponse(
            id=book.id,
            title=book.title,
            rating=float(book.rating) if book.rating else None,
            description=book.description,
            published_year=book.published_year,
            genres=[GenreBase(id=genre.id, name=genre.name) for genre in book.genres],
            contributors=contributors_with_roles,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )
        book_responses.append(book_response)

    return {
        "items": book_responses,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }


@router.get("/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: str, db: Session = Depends(get_db)):
    """Получает книгу по ID.

    Args:
        book_id: UUID книги.
        db: Сессия базы данных.

    Returns:
        BookResponse: Найденная книга.

    Raises:
        HTTPException: 400 - если неверный формат ID.
        HTTPException: 404 - если книга не найдена.
    """
    try:
        uuid.UUID(book_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book ID format"
        )

    book = (
        db.query(Book)
        .options(joinedload(Book.genres), joinedload(Book.contributors))
        .filter(Book.id == book_id)
        .first()
    )

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    contributors_with_roles = []
    for contributor in book.contributors:
        association = (
            db.query(book_contributor)
            .filter(
                book_contributor.c.book_id == book.id,
                book_contributor.c.contributor_id == contributor.id,
            )
            .first()
        )

        if association:
            contributors_with_roles.append(
                ContributorResponse(
                    id=contributor.id,
                    full_name=contributor.full_name,
                    role=association.role,
                )
            )

    return BookResponse(
        id=book.id,
        title=book.title,
        rating=float(book.rating) if book.rating else None,
        description=book.description,
        published_year=book.published_year,
        genres=[GenreBase(id=genre.id, name=genre.name) for genre in book.genres],
        contributors=contributors_with_roles,
        created_at=book.created_at,
        updated_at=book.updated_at,
    )


@router.put("/books/{book_id}", response_model=BookResponse)
async def update_book(
    book_id: str, book_data: BookUpdate, db: Session = Depends(get_db)
):
    """Обновляет книгу.

    Args:
        book_id: UUID книги.
        book_data: Данные для обновления.
        db: Сессия базы данных.

    Returns:
        BookResponse: Обновленная книга.

    Raises:
        HTTPException: 400 - если неверный формат ID или конфликт названия.
        HTTPException: 404 - если книга не найдена.
    """
    try:
        uuid.UUID(book_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book ID format"
        )

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    if book_data.title and book_data.title != book.title:
        existing_book = (
            db.query(Book)
            .filter(
                and_(
                    func.lower(Book.title) == func.lower(book_data.title),
                    Book.id != book_id,
                )
            )
            .first()
        )
        if existing_book:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Book with this title already exists",
            )

    update_data = book_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field not in ["genre_ids", "contributors"]:
            setattr(book, field, value)

    db.flush()

    if "genre_ids" in update_data:
        db.execute(book_genre.delete().where(book_genre.c.book_id == book_id))
        for genre_id in update_data["genre_ids"]:
            stmt = book_genre.insert().values(book_id=book_id, genre_id=str(genre_id))
            db.execute(stmt)

    if "contributors" in update_data:
        contributor_ids = [c.contributor_id for c in update_data["contributors"]]
        existing_contributors = (
            db.query(Contributor).filter(Contributor.id.in_(contributor_ids)).all()
        )
        if len(existing_contributors) != len(contributor_ids):
            missing_ids = set(contributor_ids) - set(
                c.id for c in existing_contributors
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"One or more contributor IDs not found: {missing_ids}",
            )

        db.execute(
            book_contributor.delete().where(book_contributor.c.book_id == book_id)
        )
        for contributor_role in update_data["contributors"]:
            stmt = book_contributor.insert().values(
                book_id=book_id,
                contributor_id=str(contributor_role.contributor_id),
                role=contributor_role.role.value,
            )
            db.execute(stmt)

    db.commit()

    book = (
        db.query(Book)
        .options(joinedload(Book.genres), joinedload(Book.contributors))
        .filter(Book.id == book_id)
        .first()
    )

    return book


@router.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: str, db: Session = Depends(get_db)):
    """Удаляет книгу.

    Args:
        book_id: UUID книги.
        db: Сессия базы данных.

    Raises:
        HTTPException: 400 - если неверный формат ID.
        HTTPException: 404 - если книга не найдена.
    """
    try:
        uuid.UUID(book_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid book ID format"
        )

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    db.execute(book_genre.delete().where(book_genre.c.book_id == book_id))
    db.execute(book_contributor.delete().where(book_contributor.c.book_id == book_id))
    db.delete(book)
    db.commit()


@router.post(
    "/genres", response_model=GenreResponse, status_code=status.HTTP_201_CREATED
)
async def create_genre(genre_data: GenreCreate, db: Session = Depends(get_db)):
    """Создает новый жанр.

    Args:
        genre_data: Данные для создания жанра.
        db: Сессия базы данных.

    Returns:
        GenreResponse: Созданный жанр.

    Raises:
        HTTPException: 400 - если жанр с таким названием уже существует.
    """
    existing_genre = (
        db.query(Genre)
        .filter(func.lower(Genre.name) == func.lower(genre_data.name))
        .first()
    )
    if existing_genre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Genre with this name already exists",
        )

    genre = Genre(id=str(uuid.uuid4()), name=genre_data.name)

    db.add(genre)
    db.commit()
    db.refresh(genre)
    return genre


@router.get("/genres", response_model=List[GenreResponse])
async def get_genres(
    q: Optional[str] = Query(None, description="Поиск жанра по названию"),
    db: Session = Depends(get_db),
):
    """Получает список жанров.

    Args:
        q: Поисковый запрос по названию жанра.
        db: Сессия базы данных.

    Returns:
        List[GenreResponse]: Список жанров.
    """
    query = db.query(Genre)

    if q:
        query = query.filter(Genre.name.ilike(f"%{q}%"))

    genres = query.order_by(Genre.name).all()
    return genres


@router.get("/genres/{genre_id}/books", response_model=dict)
async def get_books_by_genre(
    genre_id: str,
    page: int = Query(1, ge=1, description="Номер страницы"),
    page_size: int = Query(10, ge=1, le=100, description="Размер страницы"),
    db: Session = Depends(get_db),
):
    """Получает книги по определенному жанру.

    Args:
        genre_id: UUID жанра.
        page: Номер страницы.
        page_size: Размер страницы.
        db: Сессия базы данных.

    Returns:
        dict: Словарь с информацией о жанре и книгами.

    Raises:
        HTTPException: 400 - если неверный формат ID жанра.
        HTTPException: 404 - если жанр не найден.
    """
    try:
        uuid.UUID(genre_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid genre ID format"
        )

    genre = db.query(Genre).filter(Genre.id == genre_id).first()
    if not genre:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found"
        )

    query = (
        db.query(Book)
        .options(joinedload(Book.genres), joinedload(Book.contributors))
        .join(book_genre)
        .filter(book_genre.c.genre_id == genre_id)
    )

    total = query.count()
    offset = (page - 1) * page_size
    books = query.offset(offset).limit(page_size).all()

    book_responses = []
    for book in books:
        contributors_with_roles = []
        for contributor in book.contributors:
            association = (
                db.query(book_contributor)
                .filter(
                    book_contributor.c.book_id == book.id,
                    book_contributor.c.contributor_id == contributor.id,
                )
                .first()
            )

            if association:
                contributors_with_roles.append(
                    ContributorResponse(
                        id=contributor.id,
                        full_name=contributor.full_name,
                        role=association.role,
                    )
                )

        book_response = BookResponse(
            id=book.id,
            title=book.title,
            rating=float(book.rating) if book.rating else None,
            description=book.description,
            published_year=book.published_year,
            genres=[GenreBase(id=g.id, name=g.name) for g in book.genres],
            contributors=contributors_with_roles,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )
        book_responses.append(book_response)

    return {
        "genre": GenreResponse(id=genre.id, name=genre.name),
        "items": book_responses,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
    }
