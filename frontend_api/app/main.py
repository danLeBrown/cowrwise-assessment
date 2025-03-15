from threading import Thread
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from threading import Thread
from shared.core.database import AdminSessionLocal, FrontendSessionLocal
from sqlalchemy.orm import Session
from app.domains.users.user_service import UserService
from shared.repositories.user_repo import UserRepo
from alembic import command
from alembic.config import Config
from shared.schemas.user_schema import UserSchema, CreateUserSchema
from shared.schemas.book_schema import BorrowedBookSchema, BookSchema, CreateBookSchema, QueryBookSchema, CreateBorrowedBookSchema
from app.domains.books.book_service import BookService
from shared.repositories.book_repo import BookRepo
from shared.repositories.borrowed_book_repo import BorrowedBookRepo
from shared.schemas.base_schema import UpdateSchema
from redis import Redis
from typing import Optional
from app.domains.books.book_listener import create_book_listener


# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

logger.info("Starting FastAPI app")

def get_db():
    db = FrontendSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_admin_db():
    db = AdminSessionLocal()
    try:
        yield db
    finally:
        db.close()

# # Create a function to run the listener in a separate thread
def run_book_listener(pubsub):
    admin_db = AdminSessionLocal()
    frontend_db = FrontendSessionLocal()
    try:
        logger.info("Starting book listener thread")
        create_book_listener(pubsub, admin_db, frontend_db)
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

    # Start the book listener in a separate thread
    listener_thread = Thread(target=run_book_listener, args=[pubsub], daemon=True)
    listener_thread.start()
    logger.info("Book listener thread started")
    
    yield
    
    # Cleanup logic (if needed)
    logger.info("Shutting down application")


app = FastAPI(debug=True, title="FrontEnd API", version="0.1.0", lifespan=lifespan)

# enroll user
@app.post("/users", response_model=UserSchema)
async def create_user(user: CreateUserSchema, db: Session = Depends(get_db)):
    user_service = UserService(redis_client, UserRepo(db))
    return user_service.create(user)

# find all available books
@app.get("/books", response_model=list[BookSchema])
async def get_books(db: Session = Depends(get_db), publisher: Optional[str] = None, category: Optional[str] = None):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.find_all_available(query=QueryBookSchema(publisher=publisher, category=category))

# get books by id
@app.get("/books/{book_id}", response_model=BookSchema)
async def get_book(book_id: str, db: Session = Depends(get_db)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.find_by_id(book_id)

# Borrow a book for days
@app.put("/books/borrow", response_model=BorrowedBookSchema)
async def borrow_book(borrow_book: CreateBorrowedBookSchema, db: Session = Depends(get_db)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.borrow_book(borrow_book)