from pydantic import BaseModel
from shared.schemas.base_schema import BaseSchema
from typing import ForwardRef, Optional
from datetime import datetime
from uuid import UUID

# Forward reference to UserSchema
UserSchema = ForwardRef("UserSchema")

class BookSchema(BaseSchema):
    title: str
    slug: str
    author: str
    publisher: str
    category: str
    status: str
    last_borrowed_at: Optional[datetime] = None

class CreateBookSchema(BaseModel):
    title: str
    author: str
    category: str
    publisher: str

class BorrowedBookSchema(BaseSchema):
    book_id: UUID
    user_id: UUID
    returned_at: datetime
    
    user: Optional[UserSchema] = None
    book: Optional[BookSchema] = None

    class ConfigDict:
        from_attributes = True  # Enable ORM mode

class CreateBorrowedBookSchema(BaseModel):
    book_id: UUID
    user_id: UUID
    days: int

class QueryBookSchema(BaseModel):
    category: Optional[str] = None
    publisher: Optional[str] = None  
    
class BorrowedBookSchemaWithoutUser(BaseModel):
    book_id: UUID
    user_id: UUID
    returned_at: datetime
    
    book: BookSchema

class UpdateBookSchema(BaseModel):
    book_id: UUID
    status: str

# Resolve the forward reference at the end of the file
from shared.schemas.user_schema import UserSchema
BookSchema.model_rebuild()
BorrowedBookSchema.model_rebuild()