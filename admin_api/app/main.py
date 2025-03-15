from threading import Thread
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, BackgroundTasks
from threading import Thread
from shared.core.database import AdminSessionLocal, FrontendSessionLocal
from sqlalchemy.orm import Session
from app.domains.users.user_service import UserService
from shared.repositories.user_repo import UserRepo
from alembic import command
from alembic.config import Config
from shared.schemas.user_schema import UserSchema, UserBorrowedBooksSchema
from shared.schemas.book_schema import BorrowedBookSchema, BookSchema, CreateBookSchema
from app.domains.books.book_service import BookService
from shared.repositories.book_repo import BookRepo
from shared.repositories.borrowed_book_repo import BorrowedBookRepo
from shared.schemas.base_schema import UpdateSchema
from redis import Redis
from app.domains.users.user_listener import create_user_listener
from app.domains.books.book_listener import borrow_book_listener

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

logger.info("Starting FastAPI app")

def get_db():
    db = AdminSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_frontend_db():
    db = FrontendSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a function to run the listener in a separate thread
def run_user_listener(pubsub):
    admin_db = AdminSessionLocal()
    frontend_db = FrontendSessionLocal()
    try:
        logger.info("Starting user listener thread")
        create_user_listener(pubsub, admin_db=admin_db, frontend_db=frontend_db)
    except Exception as e:
        logger.error(f"Error in user listener thread: {e}")
    finally:
        admin_db.close()
        frontend_db.close()

def run_book_listener(pubsub):
    admin_db = AdminSessionLocal()
    frontend_db = FrontendSessionLocal()
    try:
        logger.info("Starting book listener thread")
        borrow_book_listener(pubsub, admin_db=admin_db, frontend_db=frontend_db)
    except Exception as e:
        logger.error(f"Error in book listener thread: {e}")
    finally:
        admin_db.close()
        frontend_db.close()

redis_client = Redis(host="redis", port=6379, db=0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")
    
    logger.info(f"Redis ping test: {redis_client.ping()}")
    pubsub = redis_client.pubsub()

    # Start the user listener in a separate thread
    listener_thread = Thread(target=run_user_listener, args=[pubsub], daemon=True)
    listener_thread.start()
    logger.info("User listener thread started")
    
    # Start the book listener in a separate thread
    book_listener_thread = Thread(target=run_book_listener, args=[pubsub], daemon=True)
    book_listener_thread.start()
    logger.info("Book listener thread started")
    
    yield
    
    # Cleanup logic (if needed)
    logger.info("Shutting down application")


app = FastAPI(debug=True, title="Admin API", version="0.1.0", lifespan=lifespan)

# Fetch / List users enrolled in the library.
@app.get("/users", response_model=list[UserSchema])
async def get_users(db: Session = Depends(get_db)):
    user_service = UserService(UserRepo(db))
    return user_service.find_all()

# Fetch / List users enrolled in the library.
@app.get("/users/borrowed-books", response_model=list[UserBorrowedBooksSchema])
async def get_users(db: Session = Depends(get_db)):
    user_service = UserService(UserRepo(db))
    return user_service.find_all_with_borrowed_books()

# Add new books to the catalogue
@app.post("/books", response_model=BookSchema)
async def create_book(book: CreateBookSchema, db: Session = Depends(get_db)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.create(book)

@app.get("/books", response_model=list[BookSchema])
async def get_books(db: Session = Depends(get_db)):
    book_service = BookService(redis_client,book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.find_all()

# Fetch/List users and the books they have borrowed
@app.get("/books/borrowed", response_model=list[BorrowedBookSchema])
async def get_borrowed_books(db: Session = Depends(get_db)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.find_borrowed_books()

# Remove a book from the catalogue.
@app.put("/books/{book_id}/unavailable", response_model=UpdateSchema)
async def update_book_status(book_id: str, db: Session = Depends(get_db)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    book_service.update_status(book_id, status="unavailable")
    
    return {"detail": "Book status updated successfully"}