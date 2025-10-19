import enum
import uuid

from sqlalchemy import (DECIMAL, CheckConstraint, Column, DateTime, Enum,
                        ForeignKey, Integer, String, Table, Text)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class RoleEnum(enum.Enum):
    """Enum, представляющий возможные роли участников.

    Атрибуты:
        author: Роль автора.
        editor: Роль редактора.
        illustrator: Роль иллюстратора.
    """

    author = "author"
    editor = "editor"
    illustrator = "illustrator"


# Связующая таблица для отношения многие-ко-многим между книгами и жанрами
book_genre = Table(
    "book_genre",
    Base.metadata,
    Column(
        "book_id",
        UUID(as_uuid=True),
        ForeignKey("book.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "genre_id",
        UUID(as_uuid=True),
        ForeignKey("genre.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# Связующая таблица для отношения многие-ко-многим между книгами и участниками с ролями
book_contributor = Table(
    "book_contributor",
    Base.metadata,
    Column(
        "book_id",
        UUID(as_uuid=True),
        ForeignKey("book.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "contributor_id",
        UUID(as_uuid=True),
        ForeignKey("contributor.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column("role", Enum(RoleEnum), primary_key=True),
)


class Book(Base):
    """Модель книги, представляющая книгу в системе.

    Атрибуты:
        id: Первичный ключ, UUID.
        title: Название книги, обязательное поле.
        rating: Рейтинг книги от 0.0 до 10.0.
        description: Описание книги.
        published_year: Год публикации книги (1450-2100).
        created_at: Временная метка создания записи.
        updated_at: Временная метка последнего обновления записи.
    """

    __tablename__ = "book"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    rating = Column(DECIMAL(3, 1))
    description = Column(Text)
    published_year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        CheckConstraint("rating >= 0.0 AND rating <= 10.0", name="rating_range"),
        CheckConstraint(
            "published_year >= 1450 AND published_year <= 2100", name="year_range"
        ),
    )


class Genre(Base):
    """Модель жанра, представляющая жанры книг.

    Атрибуты:
        id: Первичный ключ, UUID.
        name: Название жанра, уникальное и обязательное поле.
        created_at: Временная метка создания записи.
        updated_at: Временная метка последнего обновления записи.
    """

    __tablename__ = "genre"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Contributor(Base):
    """Модель участника, представляющая людей, участвующих в создании книг.

    Атрибуты:
        id: Первичный ключ, UUID.
        full_name: Полное имя участника, обязательное поле.
        created_at: Временная метка создания записи.
        updated_at: Временная метка последнего обновления записи.
    """

    __tablename__ = "contributor"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
