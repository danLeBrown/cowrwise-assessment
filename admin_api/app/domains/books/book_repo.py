from sqlalchemy.orm import Session
from app.domains.books.book_models import Book

class BookRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, book: Book) -> Book:
        self.db.add(book)
        self.db.commit()
        self.db.refresh(book)
        return book

    def find_by_id(self, id: str) -> Book:
        return self.db.query(Book).filter(Book.id == id).first()
