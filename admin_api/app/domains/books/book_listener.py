from shared.repositories.borrowed_book_repo import BorrowedBookRepo
from shared.models.book_models import BorrowedBook, Book
from sqlalchemy.orm import Session, make_transient
from redis import client
import time
import logging

logger = logging.getLogger(__name__)

def borrow_book_listener(pubsub: client.PubSub, admin_db: Session, frontend_db: Session):
    logger.info("borrow_book_listener started")
    pubsub.subscribe("book.borrowed")
    frontend_repo = BorrowedBookRepo(frontend_db)
    admin_repo = BorrowedBookRepo(admin_db)
    try:
        while True:
            message = pubsub.get_message(ignore_subscribe_messages=True)
            if message and message["channel"].decode("utf-8") == "book.borrowed":
                logger.info(f"Received message: {message}")
                borrowed_book_id = message["data"].decode("utf-8")

                borrowed_book = frontend_repo.db.query(BorrowedBook).filter(BorrowedBook.id == borrowed_book_id).first()
                
                if not borrowed_book:
                    logger.warning(f"Borrowed Book {borrowed_book_id} not found in frontend database")
                    continue
               
                frontend_db.expunge(borrowed_book)
                make_transient(borrowed_book)

                admin_repo.create(borrowed_book)

                # Update the book status in the admin database
                book = admin_db.query(Book).filter(Book.id == borrowed_book.book_id).first()
                
                if not book:
                    logger.warning(f"Book {borrowed_book.book_id} not found in admin database")
                    continue

                book.status = 'borrowed'
                book.last_borrowed_at = borrowed_book.created_at
                admin_db.commit()

                logger.info(f"Borrowed Book {borrowed_book_id} updated in admin database")            

            # Add a small delay to prevent CPU overuse
            time.sleep(0.1)
    except Exception as e:
        logger.error(f"Error in user listener: {e}")