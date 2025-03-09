from pydantic import BaseModel

class CreateBook(BaseModel):
    title: str
    author: str
    category: str

class BorrowBook(BaseModel):
    book_id: str
    user_id: str