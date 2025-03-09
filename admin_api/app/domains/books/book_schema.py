from pydantic import BaseModel
from app.shared.schema import BaseSchema
from typing import ForwardRef

# Forward reference to UserSchema
UserSchema = ForwardRef("UserSchema")

class BookSchema(BaseSchema):
    title: str
    slug: str
    author: str
    category: str

class CreateBookSchema(BaseModel):
    title: str
    author: str
    category: str

class BorrowBookSchema(BaseSchema):
    book_id: str
    user_id: str
    
    user: UserSchema = None
    book: BookSchema = None

    class ConfigDict:
        from_attributes = True  # Enable ORM mode

# Resolve the forward reference at the end of the file
from app.domains.users.user_schema import UserSchema
BookSchema.model_rebuild()
BorrowBookSchema.model_rebuild()