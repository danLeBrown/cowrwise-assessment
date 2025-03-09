from sqlalchemy import String, Column, Integer, UUID, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    slug = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    last_borrowed_at = Column(DateTime, nullable=True)
    
    # Use DateTime for timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Automatically set to the current timestamp on insert
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Automatically set to the current timestamp on insert
        onupdate=func.now(),        # Automatically update to the current timestamp on update
    )
    
class BorrowedBook(Base):
    __tablename__ = "borrowed_books"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    returned_at = Column(DateTime, nullable=False)
    
    # Use DateTime for timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Automatically set to the current timestamp on insert
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Automatically set to the current timestamp on insert
        onupdate=func.now(),        # Automatically update to the current timestamp on update
    )