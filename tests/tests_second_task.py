# tests/tests_second_task.py
import pytest
import uuid
from fastapi.testclient import TestClient
import os
from api.core.database import get_db
from main import app

client = TestClient(app)

class TestBookCRUD:
    """CRUD тесты для книг (с работающей PostgreSQL)"""
    
    def test_create_book(self):
        """CREATE книга"""
        unique_title = f"Test Book_{uuid.uuid4().hex[:8]}"
        book_data = {
            "title": unique_title,
            "rating": 8.5,
            "description": "Test description",
            "published_year": 2023
        }
        response = client.post("/api/v1/books", json=book_data)
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == unique_title
        assert "id" in data

    def test_get_book_by_id(self):
        """READ книга по ID"""
        unique_title = f"Book to Get_{uuid.uuid4().hex[:8]}"
        book_data = {"title": unique_title, "rating": 7.5}
        create_response = client.post("/api/v1/books", json=book_data)
        book_id = create_response.json()["id"]
        
        response = client.get(f"/api/v1/books/{book_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == book_id
        assert data["title"] == unique_title

    def test_get_all_books(self):
        """READ все книги"""
        unique_id1 = uuid.uuid4().hex[:8]
        unique_id2 = uuid.uuid4().hex[:8]
        
        client.post("/api/v1/books", json={"title": f"Book 1_{unique_id1}", "rating": 7.0})
        client.post("/api/v1/books", json={"title": f"Book 2_{unique_id2}", "rating": 8.0})
        
        response = client.get("/api/v1/books")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2
        assert len(data["items"]) >= 2

    def test_update_book(self):
        """UPDATE книга"""
        unique_title_old = f"Old Title_{uuid.uuid4().hex[:8]}"
        unique_title_new = f"New Title_{uuid.uuid4().hex[:8]}"
        
        create_resp = client.post("/api/v1/books", json={"title": unique_title_old, "rating": 7.0})
        book_id = create_resp.json()["id"]
        
        update_resp = client.put(f"/api/v1/books/{book_id}", json={"title": unique_title_new})
        assert update_resp.status_code == 200
        assert update_resp.json()["title"] == unique_title_new

    def test_delete_book(self):
        """DELETE книга"""
        unique_title = f"To Delete_{uuid.uuid4().hex[:8]}"
        create_resp = client.post("/api/v1/books", json={"title": unique_title, "rating": 7.0})
        book_id = create_resp.json()["id"]
        
        delete_resp = client.delete(f"/api/v1/books/{book_id}")
        assert delete_resp.status_code == 204
        
        get_resp = client.get(f"/api/v1/books/{book_id}")
        assert get_resp.status_code == 404

class TestGenreCRUD:
    """CRUD тесты для жанров"""
    
    def test_create_genre(self):
        """CREATE жанр"""
        # Используем уникальное имя для каждого теста
        unique_name = f"Fantasy_{uuid.uuid4().hex[:8]}"
        response = client.post("/api/v1/genres", json={"name": unique_name})
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == unique_name
        assert "id" in data

    def test_get_all_genres(self):
        """READ все жанры"""
        # Используем уникальные имена
        unique_id1 = uuid.uuid4().hex[:8]
        unique_id2 = uuid.uuid4().hex[:8]
        
        client.post("/api/v1/genres", json={"name": f"Fantasy_{unique_id1}"})
        client.post("/api/v1/genres", json={"name": f"Sci-Fi_{unique_id2}"})
        
        response = client.get("/api/v1/genres")
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2 
        
 # Может быть больше из-за предыдущих тестов
class TestContributorCRUD:
    """CRUD тесты для контрибьюторов"""
    
    def test_create_contributor(self):
        """CREATE контрибьютор"""
        response = client.post("/api/v1/contributors", json={"full_name": "John Doe"})
        assert response.status_code == 201
        data = response.json()
        assert data["full_name"] == "John Doe"
        assert "id" in data

    def test_get_contributor_by_id(self):
        """READ контрибьютор по ID"""
        create_resp = client.post("/api/v1/contributors", json={"full_name": "Jane Smith"})
        contributor_id = create_resp.json()["id"]
        
        response = client.get(f"/api/v1/contributors/{contributor_id}")
        assert response.status_code == 200
        assert response.json()["full_name"] == "Jane Smith"

    def test_get_all_contributors(self):
        """READ все контрибьюторы"""
        client.post("/api/v1/contributors", json={"full_name": "Author One"})
        client.post("/api/v1/contributors", json={"full_name": "Editor Two"})
        
        response = client.get("/api/v1/contributors")
        assert response.status_code == 200
        assert len(response.json()) >= 2

class TestBookWithRelationships:
    """Тесты для книг со связями"""
    
    def test_create_book_with_genres_and_contributors(self):
        """CREATE книга с жанрами и контрибьюторами"""
        unique_id = str(uuid.uuid4())[:8]

        genre1 = client.post("/api/v1/genres", json={"name": f"Fantasy_{unique_id}"}).json()
        genre2 = client.post("/api/v1/genres", json={"name": f"Adventure_{unique_id}"}).json()

        author = client.post("/api/v1/contributors", json={"full_name": f"Test Author_{unique_id}"}).json()
        editor = client.post("/api/v1/contributors", json={"full_name": f"Test Editor_{unique_id}"}).json()

        book_data = {
            "title": f"Complete Book_{unique_id}",
            "rating": 9.0,
            "published_year": 2024,
            "genre_ids": [genre1["id"], genre2["id"]],
            "contributors": [
                {"contributor_id": author["id"], "role": "author"},
                {"contributor_id": editor["id"], "role": "editor"}
            ]
        }

        response = client.post("/api/v1/books", json=book_data)
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == f"Complete Book_{unique_id}"
        assert len(data["genres"]) == 2
        assert len(data["contributors"]) == 2