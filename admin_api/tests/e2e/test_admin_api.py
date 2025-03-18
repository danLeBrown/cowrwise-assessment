import pytest
from time import sleep

@pytest.fixture
def book_data():
    return {
        "title": "Angels & Demons",
        "author": "Dan Brown",
        "category": "Fiction",
        "publisher": "Penguin"
    }

def test_create_book_syncs_between_services(admin_client, frontend_client, book_data):
    # Create book through admin API
    admin_response = admin_client.post("/books", json=book_data)
    assert admin_response.status_code == 200
    created_book = admin_response.json()
    assert created_book["title"] == book_data["title"]
    
    # Small delay to allow Redis pub/sub to propagate
    sleep(0.1)
    
    # Verify book appears in frontend API
    frontend_response = frontend_client.get("/books")
    assert frontend_response.status_code == 200
    frontend_books = frontend_response.json()
    assert len(frontend_books) == 1
    assert frontend_books[0]["title"] == book_data["title"]

def test_borrow_book_updates_both_services(admin_client, frontend_client, book_data):
    # Create a book first
    admin_response = admin_client.post("/books", json=book_data)
    book_id = admin_response.json()["id"]
    
    # Small delay to allow Redis pub/sub to propagate
    sleep(0.1)
    
    # Borrow the book through frontend API
    borrow_response = frontend_client.post(f"/books/{book_id}/borrow", json={"user_id": "test_user"})
    assert borrow_response.status_code == 200
    
    # Verify book is unavailable in both services
    admin_book = admin_client.get(f"/books/{book_id}").json()
    assert admin_book["is_available"] == False
    
    frontend_book = frontend_client.get(f"/books/{book_id}").json()
    assert frontend_book["is_available"] == False

def test_admin_book_deletion_removes_from_frontend(admin_client, frontend_client, book_data):
    # Create a book
    admin_response = admin_client.post("/books", json=book_data)
    book_id = admin_response.json()["id"]
    
    sleep(0.1)  # Allow sync
    
    # Delete through admin API
    delete_response = admin_client.delete(f"/books/{book_id}")
    assert delete_response.status_code == 200
    
    sleep(0.1)  # Allow sync
    
    # Verify book is gone from both services
    admin_response = admin_client.get(f"/books/{book_id}")
    assert admin_response.status_code == 404
    
    frontend_response = frontend_client.get(f"/books/{book_id}")
    assert frontend_response.status_code == 404