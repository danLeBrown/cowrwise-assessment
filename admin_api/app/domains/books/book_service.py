from shared.repositories.book_repo import BookRepo
from shared.repositories.borrowed_book_repo import BorrowedBookRepo
from shared.schemas.book_schema import CreateBookSchema, BorrowBookSchema
from shared.models.book_models import Book
from fastapi import HTTPException
from shared.utils.string import slugify

class BookService:
    def __init__(self, book_repo: BookRepo, borrowed_book_repo: BorrowedBookRepo):
        self.book_repo = book_repo
        self.borrowed_book_repo = borrowed_book_repo

    def create(self, book: CreateBookSchema) -> Book:
        slug = slugify(book.title)
        
        book_exists = self.book_repo.find_by_slug(slug)
        
        if book_exists:
            raise HTTPException(status_code=400, detail="Book already exists")
        
        book = Book(title=book.title, author=book.author, publisher=book.publisher, category=book.category, slug=slug, status='available')
        return self.book_repo.create(book)
    
    def borrow(self, borrow: BorrowBookSchema) -> Book:
        book = self.book_repo.find_by_id(borrow.book_id)
        
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book_is_borrowed = self.borrowed_book_repo.find_by_book_id(borrow.book_id)
        
        if book_is_borrowed.user_id == borrow.user_id:
            raise HTTPException(status_code=400, detail="You already borrowed this book")
        
        if book_is_borrowed:
            raise HTTPException(status_code=400, detail="Book is already borrowed")
        
        return self.borrowed_book_repo.create(BorrowBookSchema(book_id=book.id, user_id=borrow.user_id))
    
    def borrowed_books(self) -> list[BorrowBookSchema]:
        return self.borrowed_book_repo.find_all()
    
    def update_status(self, book_id: str, status: str) -> Book:
        book = self.book_repo.find_by_id(book_id)

        if not book:
            raise HTTPException(status_code=404, detail="Book not found")

        book.status = status
        return self.book_repo.update(book)

    def find_all(self) -> list[Book]:
        return self.book_repo.find_all()
        