from sqlalchemy import Column, String, Integer, DECIMAL, Text, DateTime, ForeignKey, Enum, Table, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import enum

Base = declarative_base()

class RoleEnum(enum.Enum):
    author = "author"
    editor = "editor"
    illustrator = "illustrator"

book_genre = Table(
    'book_genre',
    Base.metadata,
    Column('book_id', String(36), ForeignKey('book.id', ondelete='CASCADE'), primary_key=True),
    Column('genre_id', String(36), ForeignKey('genre.id', ondelete='CASCADE'), primary_key=True)
)

book_contributor = Table(
    'book_contributor',
    Base.metadata,
    Column('book_id', String(36), ForeignKey('book.id', ondelete='CASCADE'), primary_key=True),
    Column('contributor_id', String(36), ForeignKey('contributor.id', ondelete='CASCADE'), primary_key=True),
    Column('role', Enum(RoleEnum), primary_key=True)
)

class Book(Base):
    __tablename__ = 'book'
    
    id = Column(String(36), primary_key=True)
    title = Column(String(255), nullable=False)
    rating = Column(DECIMAL(3, 1))
    description = Column(Text)
    published_year = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        CheckConstraint('rating >= 0.0 AND rating <= 10.0', name='rating_range'),
        CheckConstraint('published_year >= 1450 AND published_year <= 2100', name='year_range'),
    )

class Genre(Base):
    __tablename__ = 'genre'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Contributor(Base):
    __tablename__ = 'contributor'
    
    id = Column(String(36), primary_key=True)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())