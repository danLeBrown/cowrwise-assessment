from shared.repositories.book_repo import BookRepo
from shared.models.book_models import Book
from sqlalchemy.orm import Session, make_transient
from redis import client
import time
import logging

logger = logging.getLogger(__name__)

def create_book_listener(pubsub: client.PubSub, admin_db: Session, frontend_db: Session):
    logger.info("create_book_listener started")
    pubsub.subscribe("book.created")
    frontend_repo = BookRepo(frontend_db)
    admin_repo = BookRepo(admin_db)
        
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                logger.info(f"Received message: {message}")
                book_id = message["data"].decode("utf-8")
                logger.info(f"Book {book_id} created")

                # Fetch the book from the admin database and add it to the frontend database            
                book = admin_repo.db.query(Book).filter(Book.id == book_id).first()
                
                if not book:
                    logger.warning(f"Book {book_id} not found in admin database")
                    continue
               
                logger.info(f"Book {book_id} found in admin database")

                # Detach the book object from the admin session
                admin_db.expunge(book)
                make_transient(book)

                frontend_repo.create(book)
                logger.info(f"book {book_id} synced to frontend database")
            
            # Add a small delay to prevent CPU overuse
            time.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in book listener: {e}")