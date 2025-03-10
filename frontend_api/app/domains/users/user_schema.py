from pydantic import BaseModel
from shared.schemas.base_schema import BaseSchema
from typing import List, ForwardRef
from pydantic import BaseModel

# Forward reference to BookSchema
BookSchema = ForwardRef("BookSchema")

class UserSchema(BaseSchema):
    email: str
    first_name: str
    last_name: str
    borrowed_books: List[BookSchema] = []

    class ConfigDict:
        from_attributes = True  # Enable ORM mode

class CreateUserSchema(BaseModel):
    first_name: str
    last_name: str
    email: str

# Resolve the forward reference at the end of the file
from app.domains.books.book_schema import BookSchema
UserSchema.model_rebuild()