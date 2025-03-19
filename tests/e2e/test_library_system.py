import time
import pytest

import pytest

@pytest.fixture(scope="function")
def test_book(start_redis_listeners, admin_client):
    book_data = {
        "title": "Clean Code",
        "author": "Robert Martin",
        "category": "technology",
        "publisher": "Prentice Hall"
    }
    response = admin_client.post("/books", json=book_data)
    book = response.json()
    time.sleep(1)  # Wait for pub/sub sync
    return book

@pytest.fixture(scope="function")
def test_user(start_redis_listeners, frontend_client):
    user_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }
    response = frontend_client.post("/users", json=user_data)
    user = response.json()
    time.sleep(1)  # Wait for pub/sub sync
    return user

def test_end_to_end_book_management(start_redis_listeners, admin_client, frontend_client):
    """Test the complete flow of book management between admin and frontend APIs"""
    # 1. Admin adds a new book
    book_data = {
        "title": "Python Testing with pytest",
        "author": "Brian Okken",
        "category": "technology",
        "publisher": "Pragmatic Bookshelf"
    }

    admin_response = admin_client.post("/books", json=book_data)
    assert admin_response.status_code == 200   

    time.sleep(2)
    
    # 2. Frontend can see the new book
    frontend_response = frontend_client.get("/books")
    assert frontend_response.status_code == 200
    books = frontend_response.json()
    assert len(books) == 1
    assert books[0]["title"] == book_data["title"]
    
def test_create_user(start_redis_listeners, admin_client, frontend_client):
    # 1. Frontend creates User
    user_data = {
        "email": "test@example.com",
        "first_name": "Test",
        "last_name": "User"
    }
    user_response = frontend_client.post("/users", json=user_data)
    assert user_response.status_code == 200
        
    time.sleep(2)

    # 2. Admin can see the new user
    admin_response = admin_client.get("/users")
    assert admin_response.status_code == 200
    users = admin_response.json()
    assert len(users) == 1
    assert users[0]["email"] == user_data["email"]

def test_borrow_book_flow(start_redis_listeners, admin_client, frontend_client, test_book, test_user):
    """Test the complete book borrowing flow"""
    # User borrows the book
    borrow_data = {
        "book_id": test_book["id"],
        "user_id": test_user["id"],
        "days": 7
    }

    frontend_response = frontend_client.put("/books/borrow", json=borrow_data)
    assert frontend_response.status_code == 200
    
    # # Wait for pub/sub sync with retry logic
    # max_retries = 10
    # retry_delay = 1
    
    time.sleep(2)
    # Book should no longer be available in frontend API
    frontend_response = frontend_client.get("/books")
    assert frontend_response.status_code == 200
    assert len(frontend_response.json()) == 0  # Book is borrowed, so not available
    
    # Admin should see the borrowed book
    time.sleep(2)

    admin_borrowed = admin_client.get("/books/borrowed")
    assert admin_borrowed.status_code == 200
    borrowed_books = admin_borrowed.json()
    assert len(borrowed_books) == 1    
    assert borrowed_books[0]["book_id"] == test_book["id"]
    
    # Check user's borrowed books in admin API
    time.sleep(2)
    admin_user_borrowed = admin_client.get("/users/borrowed-books")
    assert admin_user_borrowed.status_code == 200
    user_borrowed_books = admin_user_borrowed.json()
    assert len(user_borrowed_books) == 1
    assert user_borrowed_books[0]['borrowed_books'][0]["book_id"] == test_book["id"]
    
    # Check specific user's borrowed books
    time.sleep(2)
    admin_user_borrowed = admin_client.get(f"/users/{test_user['id']}/borrowed-books")
    assert admin_user_borrowed.status_code == 200
    user_borrowed_books = admin_user_borrowed.json()
    assert len(user_borrowed_books['borrowed_books']) == 1
    assert user_borrowed_books['borrowed_books'][0]["book_id"] == test_book["id"]

    # Check book status in frontend API
    time.sleep(2)
    frontend_response = frontend_client.get(f"/books/{test_book['id']}")
    assert frontend_response.status_code == 200
    book = frontend_response.json()
    assert book["status"] == "borrowed"

def test_book_filtering(start_redis_listeners, admin_client, frontend_client):
    """Test book filtering capabilities in the frontend API"""
    # Add multiple books through admin API
    books = [
        {
            "title": "Clean Code",
            "author": "Robert Martin",
            "category": "technology",
            "publisher": "Prentice Hall"
        },
        {
            "title": "Dune",
            "author": "Frank Herbert",
            "category": "fiction",
            "publisher": "Ace Books"
        },
        {
            "title": "Brief History of Time",
            "author": "Stephen Hawking",
            "category": "science",
            "publisher": "Bantam Books"
        }
    ]
    
    for book in books:
        admin_client.post("/books", json=book)
    
    time.sleep(2)

    # Test filtering by category
    tech_books = frontend_client.get("/books?category=technology")
    assert len(tech_books.json()) == 1
    assert tech_books.json()[0]["title"] == "Clean Code"
    
    # Test filtering by publisher
    bantam_books = frontend_client.get("/books?publisher=Bantam Books")
    assert len(bantam_books.json()) == 1
    assert bantam_books.json()[0]["title"] == "Brief History of Time"