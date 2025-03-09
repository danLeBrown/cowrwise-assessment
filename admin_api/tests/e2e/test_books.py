def test_create_book(client):
    response = client.post(
        "/books",
        json={"title": "Angles & Demons", "author": "Dan Brown", "category": "Fiction"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Angles & Demons"


def test_get_books(client):
    # Create a book first
    client.post(
        "/books",
        json={"title": "Angles & Demons", "author": "Dan Brown", "category": "Fiction"},
    )
    # Get all books
    response = client.get("/books")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_update_book_as_unavailable(client):
    # Create a book first
    response = client.post(
        "/books",
        json={"title": "Digital Fortress", "author": "Dan Brown", "category": "Fiction"},
    )
    id = response.json()['id']
    response = client.put("books/%s/unavailable" % (id))
    assert response.status_code == 200
    