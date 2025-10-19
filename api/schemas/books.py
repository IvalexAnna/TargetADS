import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import (BaseModel, ConfigDict, condecimal, conint,
                      field_serializer)

from api.core.database import RoleEnum


class GenreBase(BaseModel):
    """Базовая схема жанра.

    Атрибуты:
        id: UUID идентификатор жанра.
        name: Название жанра.
    """

    id: uuid.UUID
    name: str

    model_config = ConfigDict(from_attributes=True)


class ContributorBase(BaseModel):
    """Базовая схема участника.

    Атрибуты:
        id: UUID идентификатор участника.
        full_name: Полное имя участника.
    """

    id: uuid.UUID
    full_name: str

    model_config = ConfigDict(from_attributes=True)


class BookBase(BaseModel):
    """Базовая схема книги.

    Атрибуты:
        title: Название книги.
        rating: Рейтинг книги от 0.0 до 10.0.
        description: Описание книги.
        published_year: Год публикации от 1450 до 2100.
    """

    title: str
    rating: Optional[condecimal(ge=0.0, le=10.0)] = None
    description: Optional[str] = None
    published_year: Optional[conint(ge=1450, le=2100)] = None


class ContributorRole(BaseModel):
    """Схема для связи книги и участника с ролью.

    Атрибуты:
        contributor_id: UUID идентификатор участника.
        role: Роль участника в создании книги.
    """

    contributor_id: uuid.UUID
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)


class BookCreate(BookBase):
    """Схема для создания книги.

    Атрибуты:
        genre_ids: Список UUID идентификаторов жанров.
        contributors: Список участников с их ролями.
    """

    genre_ids: Optional[List[uuid.UUID]] = None
    contributors: Optional[List[ContributorRole]] = None


class BookUpdate(BaseModel):
    """Схема для обновления книги.

    Атрибуты:
        title: Название книги.
        rating: Рейтинг книги от 0.0 до 10.0.
        description: Описание книги.
        published_year: Год публикации от 1450 до 2100.
        genre_ids: Список UUID идентификаторов жанров.
        contributors: Список участников с их ролями.
    """

    title: Optional[str] = None
    rating: Optional[condecimal(ge=0.0, le=10.0)] = None
    description: Optional[str] = None
    published_year: Optional[conint(ge=1450, le=2100)] = None
    genre_ids: Optional[List[uuid.UUID]] = None
    contributors: Optional[List[ContributorRole]] = None


class ContributorResponse(ContributorBase):
    """Схема ответа для участника с ролью.

    Атрибуты:
        role: Роль участника в конкретной книге.
    """

    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)


class BookResponse(BookBase):
    """Схема ответа для книги.

    Атрибуты:
        id: UUID идентификатор книги.
        genres: Список жанров книги.
        contributors: Список участников с их ролями.
        created_at: Временная метка создания записи.
        updated_at: Временная метка последнего обновления записи.
    """

    id: uuid.UUID
    genres: List[GenreBase] = []
    contributors: List[ContributorResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("rating")
    def serialize_rating(self, rating: Decimal) -> float:
        """Конвертировать Decimal в float для JSON-сериализации."""
        return float(rating)


class GenreCreate(BaseModel):
    """Схема для создания жанра.

    Атрибуты:
        name: Название жанра.
    """

    name: str


class GenreResponse(GenreBase):
    """Схема ответа для жанра.

    Атрибуты:
        created_at: Временная метка создания записи.
        updated_at: Временная метка последнего обновления записи.
    """

    created_at: datetime
    updated_at: datetime


class ContributorCreate(BaseModel):
    """Схема для создания участника.

    Атрибуты:
        full_name: Полное имя участника.
    """

    full_name: str
