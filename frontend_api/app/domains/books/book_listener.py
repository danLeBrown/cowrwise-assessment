from shared.repositories.book_repo import BookRepo
from shared.models.book_models import Book
from sqlalchemy.orm import Session, make_transient
from shared.utils.redis_service import RedisService
import json
import time
import logging

logger = logging.getLogger(__name__)

def create_book(message: dict, admin_db: Session, frontend_repo: BookRepo):
    book_id = message["data"]

    book = admin_db.query(Book).filter(Book.id == book_id).first()

    if not book:
        logger.warning(f"Book {book_id} not found in admin database")
        return

    admin_db.expunge(book)
    make_transient(book)

    frontend_repo.create(book)
    logger.info(f"Book {book.id} created in frontend database")

def update_book(message: dict, admin_db: Session, frontend_repo: BookRepo):
    book_id = message["data"]

    admin_book = admin_db.query(Book).filter(Book.id == book_id).first()

    if not admin_book:
        logger.warning(f"Book {book_id} not found in admin database")
        return

    book = frontend_repo.find_by_id(book_id)

    if not book:
        logger.warning(f"Book {book_id} not found in frontend database")
        return
    
    book.status = admin_book.status
    frontend_repo.db.commit()

    logger.info(f"Book {book.id} updated in frontend database")

def book_listener(redis_client: RedisService, admin_db: Session, frontend_db: Session):
    logger.info("book_listener started")
    pubsub = redis_client.client.pubsub()
    pubsub.subscribe("book.created", "book.updated")
 
    frontend_repo = BookRepo(frontend_db)
        
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message and message["type"] == "message" and message["channel"] in ["book.created", "book.updated"]:
                logger.info(f"Received message: {message}")
                channel = message["channel"]

                if channel == "book.created":
                    create_book(message, admin_db, frontend_repo)
                
                if channel == "book.updated":
                    update_book(message, admin_db, frontend_repo)
                
            # Add a small delay to prevent CPU overuse
            time.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in book listener: {e}")
        raise
