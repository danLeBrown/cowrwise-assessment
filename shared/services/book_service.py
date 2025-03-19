from shared.repositories.book_repo import BookRepo
from shared.repositories.borrowed_book_repo import BorrowedBookRepo
from shared.schemas.book_schema import CreateBookSchema, BorrowedBookSchema, QueryBookSchema, UpdateBookSchema
from shared.models.book_models import Book
from fastapi import HTTPException, logger
from shared.utils.redis_service import RedisService
from shared.utils.string import slugify
from redis import Redis
from shared.schemas.book_schema import BorrowedBookSchema, CreateBorrowedBookSchema
from shared.models.book_models import Book, BorrowedBook
from fastapi import HTTPException
from datetime import datetime, timedelta

class BookService:
    def __init__(self, redis_client: RedisService, book_repo: BookRepo, borrowed_book_repo: BorrowedBookRepo):
        self.redis_client = redis_client
        self.book_repo = book_repo
        self.borrowed_book_repo = borrowed_book_repo

    def find_by_id(self, book_id: str) -> Book:
        return self.book_repo.find_by_id(book_id)
    
    def find_all(self, query: QueryBookSchema) -> list[Book]:
        # query params are optional
        if not query.category and not query.publisher:
            return self.book_repo.find_all()

        if query.category and not query.publisher:
            return self.book_repo.db.query(Book).filter(Book.category == query.category).all()
        
        if not query.category and query.publisher:
            return self.book_repo.db.query(Book).filter(Book.publisher == query.publisher).all()
        
        return self.book_repo.db.query(Book).filter(Book.category == query.category, Book.publisher == query.publisher).all()
    
    def find_all_available(self, query:QueryBookSchema) -> list[Book]:
        # query params are optional
        if not query.category and not query.publisher:
            return self.book_repo.db.query(Book).filter(Book.last_borrowed_at == None, Book.status == 'available').all()
        
        if query.category and not query.publisher:
            return self.book_repo.db.query(Book).filter(Book.category == query.category, Book.last_borrowed_at == None, Book.status == 'available').all()
        
        if not query.category and query.publisher:
            return self.book_repo.db.query(Book).filter(Book.publisher == query.publisher, Book.last_borrowed_at == None, Book.status == 'available').all()
        
        return self.book_repo.db.query(Book).filter(Book.category == query.category, Book.publisher == query.publisher, Book.last_borrowed_at == None, Book.status == 'available').all()

    def create(self, book: CreateBookSchema) -> Book:
        slug = slugify(book.title)
        
        book_exists = self.book_repo.find_by_slug(slug)
        
        if book_exists:
            raise HTTPException(status_code=400, detail="Book already exists")
        
        book = Book(title=book.title, author=book.author, publisher=book.publisher, category=book.category, slug=slug, status='available')
        book = self.book_repo.create(book)
        
        self.redis_client.client.publish("book.created", str(book.id))

        return book
        
    
    # def borrow(self, borrow: BorrowedBookSchema) -> Book:
    #     book = self.book_repo.find_by_id(borrow.book_id)
        
    #     if not book:
    #         raise HTTPException(status_code=404, detail="Book not found")
        
    #     book_is_borrowed = self.borrowed_book_repo.find_by_book_id(borrow.book_id)
        
    #     if book_is_borrowed.user_id == borrow.user_id:
    #         raise HTTPException(status_code=400, detail="You already borrowed this book")
        
    #     if book_is_borrowed:
    #         raise HTTPException(status_code=400, detail="Book is already borrowed")
        
    #     return self.borrowed_book_repo.create(BorrowedBookSchema(book_id=book.id, user_id=borrow.user_id))
    
    def update_status(self, request: UpdateBookSchema) -> Book:
        book = self.book_repo.find_by_id(request.book_id)

        if request.status not in ['available', 'borrowed', 'unavailable']:
            raise HTTPException(status_code=400, detail="Invalid status")

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        book.status = request.status
        update = self.book_repo.update(book)

        self.redis_client.client.publish("book.updated", str(book.id))

        return update

    def find_all(self) -> list[Book]:
        return self.book_repo.find_all()
    
    def find_borrowed_books(self) -> list[BorrowedBook]:
        return self.borrowed_book_repo.find_all()
    
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
        
        self.redis_client.client.publish("book.borrowed", str(borrowed_book.id))

        return borrowed_book
    
    def user_borrowed_books(self, user_id: str) -> list[BorrowedBookSchema]:
        return self.borrowed_book_repo.find_by_user_id(user_id)    