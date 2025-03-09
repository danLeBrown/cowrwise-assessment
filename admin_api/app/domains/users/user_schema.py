from pydantic  import BaseModel
from app.shared.models import BaseSchema

class User(BaseSchema):
    email: str
    first_name: str
    last_name: str

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    email: str
