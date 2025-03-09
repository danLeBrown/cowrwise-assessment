from sqlalchemy import String, Column, Integer, UUID, ForeignKey, DateTime
from sqlalchemy.sql import func
from app.core.database import Base
import uuid  # For generating UUIDs in Python

class Book(Base):
    __tablename__ = "books"
    
        # Use UUID as the primary key
    id = Column(
        UUID(as_uuid=True),  # Use UUID type for PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # Automatically generate a UUID for new records
        unique=True,
        index=True,
    )
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
    
        # Use UUID as the primary key
    id = Column(
        UUID(as_uuid=True),  # Use UUID type for PostgreSQL
        primary_key=True,
        default=uuid.uuid4,  # Automatically generate a UUID for new records
        unique=True,
        index=True,
    )
    # Foreign key to Book (UUID)
    book_id = Column(
        UUID(as_uuid=True),
        ForeignKey("books.id"),
        nullable=False,
    )
    # Foreign key to User (UUID)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
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