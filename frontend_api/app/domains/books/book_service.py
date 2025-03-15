from shared.repositories.book_repo import BookRepo
from shared.repositories.borrowed_book_repo import BorrowedBookRepo
from shared.schemas.book_schema import BorrowedBookSchema, CreateBorrowedBookSchema
from shared.models.book_models import Book, BorrowedBook
from fastapi import HTTPException
from shared.utils.string import slugify
from redis import Redis
from shared.services.book_service import BaseBookService
from datetime import datetime, timedelta

class BookService(BaseBookService):
    def __init__(self, redis_client: Redis, book_repo: BookRepo, borrowed_book_repo: BorrowedBookRepo):
        self.redis_client = redis_client
        self.book_repo = book_repo
        self.borrowed_book_repo = borrowed_book_repo
    
    def borrow_book(self, borrow: CreateBorrowedBookSchema) -> Book:
        book = self.book_repo.find_by_id(borrow.book_id)
        
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book_is_borrowed = self.borrowed_book_repo.find_by_book_id(borrow.book_id)
        
        if book_is_borrowed:
            if book_is_borrowed.user_id == borrow.user_id:
                raise HTTPException(status_code=400, detail="You already borrowed this book")
            raise HTTPException(status_code=400, detail="Book is already borrowed")
        
        
        # returned_at is the start of today's date + no of days to return the book
        returned_at = datetime.now() + timedelta(days=borrow.days)
        borrowed_book =  self.borrowed_book_repo.create(BorrowedBook(book_id=book.id, user_id=borrow.user_id, returned_at=returned_at))
        
        book.last_borrowed_at = borrowed_book.created_at
        book.status = 'borrowed'
        self.book_repo.update(book)
        
        self.redis_client.publish("book.borrowed", str(borrowed_book.id))

        return borrowed_book
    
    def user_borrowed_books(self, user_id: str) -> list[BorrowedBookSchema]:
        return self.borrowed_book_repo.find_by_user_id(user_id)    