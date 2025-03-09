from sqlalchemy.orm import Session
from app.domains.books.book_models import BorrowedBook


class BorrowedBookRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, borrowed_book: BorrowedBook) -> BorrowedBook:
        self.db.add(borrowed_book)
        self.db.commit()
        self.db.refresh(borrowed_book)
        return borrowed_book
    
    def find_all(self) -> list[BorrowedBook]:
        return self.db.query(BorrowedBook).all()
    
    def find_by_book_id(self, book_id: str) -> BorrowedBook:
        return self.db.query(BorrowedBook).filter(BorrowedBook.book_id == book_id).first()