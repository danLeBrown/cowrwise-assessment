from sqlalchemy import String, Column, UUID, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from uuid import uuid4

class Book(Base):
    __tablename__ = "books"

    # Use UUID as the primary key
    id = Column(
        UUID(as_uuid=True),  # Use UUID type for PostgreSQL
        primary_key=True,
        default=uuid4,  # Automatically generate a UUID for new records
        unique=True,
        index=True,
    )

    # Use DateTime for timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Automatically set to the current timestamp on insert
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Automatically set to the current timestamp on insert
        onupdate=func.now(),  # Automatically update to the current timestamp on update
    )

    title = Column(String, index=True, nullable=False)
    slug = Column(String, index=True, nullable=False)
    status = Column(String, index=True, nullable=False)
    author = Column(String, index=True, nullable=False)
    category = Column(String, index=True, nullable=False)
    last_borrowed_at = Column(DateTime, nullable=True)
    
    # Define a one-to-many relationship with BorrowedBook
    borrowed_books = relationship("BorrowedBook", back_populates="book")
    
    
class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    # Use UUID as the primary key
    id = Column(
        UUID(as_uuid=True),  # Use UUID type for PostgreSQL
        primary_key=True,
        default=uuid4,  # Automatically generate a UUID for new records
        unique=True,
        index=True,
    )

    # Use DateTime for timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Automatically set to the current timestamp on insert
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Automatically set to the current timestamp on insert
        onupdate=func.now(),  # Automatically update to the current timestamp on update
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
    
    # Define many-to-one relationships with User and Book
    user = relationship("User", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_books")
