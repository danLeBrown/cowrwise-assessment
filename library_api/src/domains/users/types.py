from pydantic import BaseModel

class CreateUser(BaseModel):
    email: str
    first_name: str
    last_name: str