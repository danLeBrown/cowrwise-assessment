from pydantic import BaseModel
from app.shared.models import BaseSchema
from uuid import UUID
from datetime import datetime

class Book(BaseSchema):
    title: str
    slug: str
    author: str
    category: str

class CreateBook(BaseModel):
    title: str
    author: str
    category: str

class BorrowBook(BaseModel):
    book_id: str
    user_id: str