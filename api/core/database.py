"""Database configuration and models."""
import uuid
from sqlalchemy import Column, String, Integer, DECIMAL, Text, DateTime, ForeignKey, Enum, Table, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import UUID
import enum

from api.core.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class RoleEnum(enum.Enum):
    author = "author"
    editor = "editor"
    illustrator = "illustrator"


book_genre = Table(
    'book_genre',
    Base.metadata,
    Column('book_id', UUID(as_uuid=True), ForeignKey(
        'book.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', UUID(as_uuid=True), ForeignKey(
        'genre.id', ondelete='CASCADE'), primary_key=True)
)

book_contributor = Table(
    'book_contributor',
    Base.metadata,
    Column('book_id', UUID(as_uuid=True), ForeignKey(
        'book.id', ondelete='CASCADE'), primary_key=True),
    Column('contributor_id', UUID(as_uuid=True), ForeignKey(
        'contributor.id', ondelete='CASCADE'), primary_key=True),
    Column('role', Enum(RoleEnum), primary_key=True)
)


class Book(Base):
    __tablename__ = 'book'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    rating = Column(DECIMAL(3, 1))
    description = Column(Text)
    published_year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(), onupdate=func.now())

    # ✅ ДОБАВИЛИ ОТНОШЕНИЯ
    genres = relationship("Genre", secondary=book_genre, backref="books")
    contributors = relationship(
        "Contributor", secondary=book_contributor, backref="books")

    __table_args__ = (
        CheckConstraint('rating >= 0.0 AND rating <= 10.0',
                        name='rating_range'),
        CheckConstraint(
            'published_year >= 1450 AND published_year <= 2100', name='year_range'),
    )


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(), onupdate=func.now())


class Contributor(Base):
    __tablename__ = 'contributor'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True),
                        server_default=func.now(), onupdate=func.now())


def get_db():
    """Dependency for getting database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
