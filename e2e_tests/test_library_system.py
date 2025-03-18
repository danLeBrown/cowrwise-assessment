def test_end_to_end_book_management(admin_client, frontend_client):
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
    book_id = admin_response.json()["id"]
    
    # 2. Frontend can see the new book
    frontend_response = frontend_client.get("/books")
    assert frontend_response.status_code == 200
    books = frontend_response.json()
    assert len(books) == 1
    assert books[0]["title"] == book_data["title"]
    
    # 3. User borrows the book
    borrow_data = {
        "book_id": book_id,
        "user_id": "test_user",
        "days": 7
    }
    borrow_response = frontend_client.put("/books/borrow", json=borrow_data)
    assert borrow_response.status_code == 200
    
    # 4. Book is no longer available in frontend API
    frontend_response = frontend_client.get("/books")
    assert frontend_response.status_code == 200
    assert len(frontend_response.json()) == 0
    
    # 5. Admin can see the borrowed book
    admin_borrowed = admin_client.get("/books/borrowed")
    assert admin_borrowed.status_code == 200
    borrowed_books = admin_borrowed.json()
    assert len(borrowed_books) == 1
    assert borrowed_books[0]["book_id"] == book_id

def test_book_filtering():
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
    
    # Test filtering by category
    tech_books = frontend_client.get("/books?category=technology")
    assert len(tech_books.json()) == 1
    assert tech_books.json()[0]["title"] == "Clean Code"
    
    # Test filtering by publisher
    bantam_books = frontend_client.get("/books?publisher=Bantam Books")
    assert len(bantam_books.json()) == 1
    assert bantam_books.json()[0]["title"] == "Brief History of Time"

def test_user_management():
    """Test user enrollment and book borrowing tracking"""
    # 1. Enroll a user
    user_data = {
        "email": "test@example.com",
        "firstname": "Test",
        "lastname": "User"
    }
    user_response = frontend_client.post("/users", json=user_data)
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]
    
    # 2. Admin adds a book
    book_data = {
        "title": "Test Book",
        "author": "Test Author",
        "category": "test",
        "publisher": "Test Publisher"
    }
    book_response = admin_client.post("/books", json=book_data)
    book_id = book_response.json()["id"]
    
    # 3. User borrows the book
    borrow_data = {
        "book_id": book_id,
        "user_id": user_id,
        "days": 7
    }
    frontend_client.put("/books/borrow", json=borrow_data)
    
    # 4. Admin can see user's borrowed books
    users_books = admin_client.get("/users/borrowed-books")
    assert users_books.status_code == 200
    user_books = users_books.json()
    assert len(user_books) == 1
    assert user_books[0]["user"]["email"] == user_data["email"]
    assert len(user_books[0]["borrowed_books"]) == 1
    assert user_books[0]["borrowed_books"][0]["book"]["title"] == book_data["title"]
