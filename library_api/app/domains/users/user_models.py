from sqlalchemy import String, Column, UUID, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from uuid import uuid4
from sqlalchemy import String, Column
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

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

    first_name = Column(String, index=True, nullable=False)
    last_name = Column(String, index=True, nullable=False)
    email = Column(String, index=True, unique=True, nullable=False)

    # Define a one-to-many relationship with BorrowedBook
    borrowed_books = relationship("BorrowedBook", back_populates="user")
