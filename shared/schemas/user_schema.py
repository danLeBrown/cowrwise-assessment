from pydantic import BaseModel
from shared.schemas.base_schema import BaseSchema
from typing import List, ForwardRef, Optional  # Add Optional here
from pydantic import BaseModel

# Forward reference to BookSchema
BorrowedBookSchemaWithoutUser = ForwardRef("BorrowedBookSchemaWithoutUser")
class UserSchema(BaseSchema):
    email: str
    first_name: str
    last_name: str

    class ConfigDict:
        from_attributes = True  # Enable ORM mode
        
class UserBorrowedBooksSchema(UserSchema):
    borrowed_books: Optional[List[BorrowedBookSchemaWithoutUser]] = []    

class CreateUserSchema(BaseModel):
    first_name: str
    last_name: str
    email: str

# Resolve the forward reference at the end of the file
from shared.schemas.book_schema import BorrowedBookSchemaWithoutUser
UserSchema.model_rebuild()