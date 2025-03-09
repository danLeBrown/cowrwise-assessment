import logging
from fastapi import FastAPI, Depends
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.domains.users.user_service import UserService
from app.domains.users.user_repo import UserRepo
from alembic import command
from alembic.config import Config
from app.domains.users.user_schema import UserSchema, CreateUserSchema
from app.domains.books.book_schema import BorrowBookSchema, BookSchema, CreateBookSchema
from app.domains.books.book_service import BookService
from app.domains.books.book_repo import BookRepo
from app.domains.books.borrowed_book_repo import BorrowedBookRepo

app = FastAPI(debug=True)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the logging level to DEBUG
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


# Call this function at startup
run_migrations()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", response_model=UserSchema)
async def create_user(user: CreateUserSchema, db: Session = Depends(get_db)):
    user_service = UserService(UserRepo(db))
    return user_service.create(user)

# Fetch / List users enrolled in the library.
@app.get("/users", response_model=list[UserSchema])
async def get_users(db: Session = Depends(get_db)):
    user_service = UserService(UserRepo(db))
    return user_service.find_all()

# Add new books to the catalogue
@app.post("/books", response_model=BookSchema)
async def create_book(book: CreateBookSchema, db: Session = Depends(get_db)):
    book_service = BookService(book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.create(book)

@app.get("/books", response_model=list[BookSchema])
async def get_books(db: Session = Depends(get_db)):
    book_service = BookService(book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.find_all()

# Fetch/List users and the books they have borrowed
@app.get("/books/borrowed", response_model=list[BorrowBookSchema])
async def get_borrowed_books(db: Session = Depends(get_db)):
    book_service = BookService(book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.borrowed_books()

# Remove a book from the catalogue.
@app.put("/books/{book_id}/unavailable")
async def update_book_status(book_id: str, db: Session = Depends(get_db)):
    book_service = BookService(book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.update_status(book_id, status="unavailable")
