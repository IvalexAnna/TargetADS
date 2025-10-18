from pydantic import BaseModel, condecimal, conint
from typing import Optional, List
from datetime import datetime
import uuid


class GenreBase(BaseModel):
    """Base genre schema."""
    id: uuid.UUID
    name: str

    class Config:
        """Pydantic config."""
        from_attributes = True


class ContributorBase(BaseModel):
    """Base contributor schema."""
    id: uuid.UUID
    full_name: str

    class Config:
        """Pydantic config."""
        from_attributes = True


class BookBase(BaseModel):
    """Base book schema."""
    title: str
    rating: Optional[condecimal(ge=0.0, le=10.0)] = None
    description: Optional[str] = None
    published_year: Optional[conint(ge=1450, le=2100)] = None


class BookCreate(BookBase):
    """Schema for creating a book."""
    genre_ids: Optional[List[uuid.UUID]] = None


class BookUpdate(BaseModel):
    """Schema for updating a book."""
    title: Optional[str] = None
    rating: Optional[condecimal(ge=0.0, le=10.0)] = None
    description: Optional[str] = None
    published_year: Optional[conint(ge=1450, le=2100)] = None
    genre_ids: Optional[List[uuid.UUID]] = None


class BookResponse(BookBase):
    """Schema for book response."""
    id: uuid.UUID
    genres: List[GenreBase] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class GenreCreate(BaseModel):
    """Schema for creating a genre."""
    name: str


class GenreResponse(GenreBase):
    """Schema for genre response."""
    created_at: datetime
    updated_at: datetime


class ContributorCreate(BaseModel):
    """Schema for creating a contributor."""
    full_name: str


class ContributorResponse(ContributorBase):
    """Schema for contributor response."""
    created_at: datetime
    updated_at: datetime
