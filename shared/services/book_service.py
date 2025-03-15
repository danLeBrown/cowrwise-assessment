from shared.repositories.book_repo import BookRepo
from shared.repositories.borrowed_book_repo import BorrowedBookRepo
from shared.schemas.book_schema import CreateBookSchema, BorrowBookSchema, QueryBookSchema
from shared.models.book_models import Book
from fastapi import HTTPException
from shared.utils.string import slugify
from redis import Redis

class BaseBookService:
    def __init__(self, redis_client: Redis, book_repo: BookRepo, borrowed_book_repo: BorrowedBookRepo):
        self.redis_client = redis_client
        self.book_repo = book_repo
        self.borrowed_book_repo = borrowed_book_repo
    
    # def borrow(self, borrow: BorrowBookSchema) -> Book:
    #     book = self.book_repo.find_by_id(borrow.book_id)
        
    #     if not book:
    #         raise HTTPException(status_code=404, detail="Book not found")
        
    #     book_is_borrowed = self.borrowed_book_repo.find_by_book_id(borrow.book_id)
        
    #     if book_is_borrowed.user_id == borrow.user_id:
    #         raise HTTPException(status_code=400, detail="You already borrowed this book")
        
    #     if book_is_borrowed:
    #         raise HTTPException(status_code=400, detail="Book is already borrowed")
        
    #     borrowed_book =  self.borrowed_book_repo.create(BorrowBookSchema(book_id=book.id, user_id=borrow.user_id))
        
    #     # self.redis_client.publish("borrowed_book.new", json.dumps(borrowed_book))
        
    #     return borrowed_book
    
    # def user_borrowed_books(self, user_id: str) -> list[BorrowBookSchema]:
    #     return self.borrowed_book_repo.find_by_user_id(user_id)    

    def find_all(self, query: QueryBookSchema) -> list[Book]:
        # query params are optional
        if not query.category and not query.publisher:
            return self.book_repo.find_all()

        if query.category and not query.publisher:
            return self.book_repo.db.query(Book).filter(Book.category == query.category).all()
        
        if not query.category and query.publisher:
            return self.book_repo.db.query(Book).filter(Book.publisher == query.publisher).all()
        
        return self.book_repo.db.query(Book).filter(Book.category == query.category, Book.publisher == query.publisher).all()
        