"""Tests for book endpoints."""
import pytest
from fastapi.testclient import TestClient
import uuid

from main import app

client = TestClient(app)


def test_create_book():
    """Test creating a book."""
    book_data = {
        "title": "Test Book",
        "rating": 8.5,
        "description": "Test description",
        "published_year": 2020
    }
    
    response = client.post("/api/v1/books", json=book_data)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Book"
    assert data["rating"] == 8.5


def test_get_books():
    """Test getting all books."""
    response = client.get("/api/v1/books")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_genre():
    """Test creating a genre."""
    genre_data = {
        "name": f"Test Genre {uuid.uuid4()}"
    }
    
    response = client.post("/api/v1/genres", json=genre_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == genre_data["name"]


def test_get_genres():
    """Test getting all genres."""
    response = client.get("/api/v1/genres")
    assert response.status_code == 200
    assert isinstance(response.json(), list)