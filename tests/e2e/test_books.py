def test_create_book(admin_client, frontend_client):
    response = admin_client.post(
        "/books",
        json={"title": "Angles & Demons", "author": "Dan Brown", "category": "Fiction", "publisher": "Penguin"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Angles & Demons"
    
    frontend_response = frontend_client.get(
        "/books"
    )
    assert frontend_response.status_code == 200
    assert len(frontend_response.json()) == 1


def test_get_books(client):
    # Create a book first
    client.post(
        "/books",
        json={"title": "Angles & Demons", "author": "Dan Brown", "category": "Fiction", "publisher": "Penguin"},
    )
    # Get all books
    response = client.get("/books")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_update_book_as_unavailable(client):
    # Create a book first
    response = client.post(
        "/books",
        json={"title": "Digital Fortress", "author": "Dan Brown", "category": "Fiction", "publisher": "Penguin"},
    )
    id = response.json()['id']
    response = client.put("books/%s/unavailable" % (id))
    assert response.status_code == 200
    