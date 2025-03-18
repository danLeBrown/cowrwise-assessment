from threading import Thread
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, BackgroundTasks
from threading import Thread
from shared.core.database import get_admin_session, get_frontend_session
from sqlalchemy.orm import Session
from shared.repositories.user_repo import UserRepo
from shared.services.user_service import UserService
from shared.schemas.user_schema import UserSchema, UserBorrowedBooksSchema
from shared.schemas.book_schema import BorrowedBookSchema, BookSchema, CreateBookSchema, UpdateBookSchema
from shared.services.book_service import BookService
from shared.repositories.book_repo import BookRepo
from shared.repositories.borrowed_book_repo import BorrowedBookRepo
from shared.schemas.base_schema import UpdateSchema
from redis import Redis
from . domains.users.user_listener import create_user_listener
from . domains.books.book_listener import borrow_book_listener
from shared.utils.redis_service import RedisService
from alembic import command
from alembic.config import Config
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

logger.info("Starting FastAPI app")


async def run_migrations():
    # alembic_cfg = Config("alembic.ini")
    # await asyncio.to_thread(command.upgrade, alembic_cfg, "head")
    return

def get_admin_db():
    db = get_admin_session()
    try:
        yield db
    finally:
        db.close()

def get_frontend_db():
    db = get_frontend_session()
    try:
        yield db
    finally:
        db.close()

# Create a function to run the listener in a separate thread
def run_user_listener(redis_client: RedisService, admin_db: Session, frontend_db: Session):
    try:
        logger.info("Starting user listener thread")
        create_user_listener(redis_client, admin_db=admin_db, frontend_db=frontend_db)
    except Exception as e:
        logger.error(f"Error in user listener thread: {e}")
    finally:
        admin_db.close()
        frontend_db.close()

def run_book_listener(redis_client: RedisService, admin_db: Session, frontend_db: Session):
    try:
        logger.info("Starting book listener thread")
        borrow_book_listener(redis_client, admin_db=admin_db, frontend_db=frontend_db)
    except Exception as e:
        logger.error(f"Error in book listener thread: {e}")
    finally:
        admin_db.close()
        frontend_db.close()

def get_redis():
    return RedisService(Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application") 
    redis_client = get_redis()
    logger.info(f"Redis ping test: {redis_client.ping()}")
    
    # Start the user listener in a separate thread
    listener_thread = Thread(target=run_user_listener, args=[redis_client, next(get_admin_db()), next(get_frontend_db())], daemon=True)
    listener_thread.start()
    logger.info("User listener thread started")
    
    # Start the book listener in a separate thread
    book_listener_thread = Thread(target=run_book_listener, args=[redis_client, next(get_admin_db()), next(get_frontend_db())], daemon=True)
    book_listener_thread.start()
    logger.info("Book listener thread started")
    
    await run_migrations()

    yield
    
    # Cleanup logic (if needed)
    logger.info("Shutting down application")


app = FastAPI(debug=True, title="Admin API", version="0.1.0", lifespan=lifespan)

# Fetch / List users enrolled in the library.
@app.get("/users", response_model=list[UserSchema])
async def get_users(db: Session = Depends(get_admin_db), redis_client: Redis = Depends(get_redis)):
    user_service = UserService(redis_client, UserRepo(db))
    return user_service.find_all()

# Fetch / List users enrolled in the library.
@app.get("/users/borrowed-books", response_model=list[UserBorrowedBooksSchema])
async def get_users(db: Session = Depends(get_admin_db), redis_client: Redis = Depends(get_redis)):
    user_service = UserService(redis_client, UserRepo(db))
    return user_service.find_all_with_borrowed_books()

# Add new books to the catalogue
@app.post("/books", response_model=BookSchema)
async def create_book(book: CreateBookSchema, db: Session = Depends(get_admin_db), redis_client: Redis = Depends(get_redis)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.create(book)

@app.get("/books", response_model=list[BookSchema])
async def get_books(db: Session = Depends(get_admin_db), redis_client: Redis = Depends(get_redis)):
    book_service = BookService(redis_client,book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.find_all()

# Fetch/List users and the books they have borrowed
@app.get("/books/borrowed", response_model=list[BorrowedBookSchema])
async def get_borrowed_books(db: Session = Depends(get_admin_db), redis_client: Redis = Depends(get_redis)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.find_borrowed_books()

# Remove a book from the catalogue.
@app.put("/books", response_model=UpdateSchema)
async def update_book(request: UpdateBookSchema, db: Session = Depends(get_admin_db), redis_client: Redis = Depends(get_redis)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    book_service.update_status(request)
    
    return {"detail": "Book status updated successfully"}