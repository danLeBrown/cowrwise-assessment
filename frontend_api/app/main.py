from threading import Thread
import logging
from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Depends
from threading import Thread
from shared.core.database import get_admin_session, get_frontend_session
from sqlalchemy.orm import Session
from shared.services.user_service import UserService
from shared.repositories.user_repo import UserRepo
from alembic import command
from alembic.config import Config
from shared.schemas.user_schema import UserSchema, CreateUserSchema
from shared.schemas.book_schema import BorrowedBookSchema, BookSchema, CreateBookSchema, QueryBookSchema, CreateBorrowedBookSchema
from shared.services.book_service import BookService
from shared.repositories.book_repo import BookRepo
from shared.repositories.borrowed_book_repo import BorrowedBookRepo
from shared.schemas.base_schema import UpdateSchema
from redis import Redis
from typing import Optional
from . domains.books.book_listener import book_listener
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
    # command.upgrade(alembic_cfg, "head")
    return

# run_migrations()

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


# # Create a function to run the listener in a separate thread
def run_listener(redis_client: RedisService, admin_db: Session, frontend_db: Session):
    try:
        logger.info("Starting book listener thread")
        book_listener(redis_client, admin_db=admin_db, frontend_db=frontend_db)
    except Exception as e:
        logger.error(f"Error in book listener thread: {e}")
    finally:
        frontend_db.close()


def get_redis():
    return RedisService(Redis(host=os.getenv("REDIS_HOST"), port=os.getenv("REDIS_PORT"), db=0, decode_responses=True,))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application")
    redis_client = get_redis()
    logger.info(f"Redis ping test: {redis_client.ping()}")
    
    # Start the book listener in a separate thread
    listener_thread = Thread(target=run_listener, args=[redis_client, next(get_admin_db()), next(get_frontend_db())], daemon=True)
    listener_thread.start()
    logger.info("Book listener thread started")
    
    # await run_migrations()
    
    yield
    
    # Cleanup logic (if needed)
    logger.info("Shutting down application")


app = FastAPI(debug=True, title="FrontEnd API", version="0.1.0", lifespan=lifespan)

@app.get('/health')
async def health(sleep: int = 0):
    time.sleep(sleep)
    return {"status": "ok"}

# enroll user
@app.post("/users", response_model=UserSchema)
async def create_user(user: CreateUserSchema, db: Session = Depends(get_frontend_db), redis_client: RedisService = Depends(get_redis)):
    user_service = UserService(redis_client, UserRepo(db))
    return user_service.create(user)

# find all available books
@app.get("/books", response_model=list[BookSchema])
async def get_books(db: Session = Depends(get_frontend_db), publisher: Optional[str] = None, category: Optional[str] = None, redis_client: RedisService = Depends(get_redis)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.find_all_available(query=QueryBookSchema(publisher=publisher, category=category))

# get books by id
@app.get("/books/{book_id}", response_model=BookSchema)
async def get_book(book_id: str, db: Session = Depends(get_frontend_db), redis_client: RedisService = Depends(get_redis)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.find_by_id(book_id)

# Borrow a book for days
@app.put("/books/borrow", response_model=BorrowedBookSchema)
async def borrow_book(borrow_book: CreateBorrowedBookSchema, db: Session = Depends(get_frontend_db), redis_client: RedisService = Depends(get_redis)):
    book_service = BookService(redis_client, book_repo=BookRepo(db), borrowed_book_repo=BorrowedBookRepo(db))
    return book_service.borrow_book(borrow_book)