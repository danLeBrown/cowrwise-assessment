from app.domains.books.book_repo import BookRepo
from app.domains.books.borrowed_book_repo import BorrowedBookRepo
from app.domains.books.book_schema import CreateBook, BorrowBook
from app.domains.books.book_models import Book
from fastapi import HTTPException
from app.domains.books.string import slugify

class BookService:
    def __init__(self, book_repo: BookRepo, borrowed_book_repo: BorrowedBookRepo):
        self.book_repo = book_repo
        self.borrowed_book_repo = borrowed_book_repo

    def create(self, book: CreateBook) -> Book:
        book = Book(title=book.title, author=book.author, category=book.category, slug=slugify(book.title))
        return self.book_repo.create(book)
    
    def borrow(self, borrow: BorrowBook) -> Book:
        book = self.book_repo.findById(borrow.book_id)
        
        if not book:
            raise HTTPException(status_code=404, detail="Book not found")
        
        book_is_borrowed = self.borrowed_book_repo.find_by_book_id(borrow.book_id)
        
        if book_is_borrowed.user_id == borrow.user_id:
            raise HTTPException(status_code=400, detail="You already borrowed this book")
        
        if book_is_borrowed:
            raise HTTPException(status_code=400, detail="Book is already borrowed")
        
        return self.borrowed_book_repo.create(BorrowBook(book_id=book.id, user_id=borrow.user_id))
        
        