from pydantic import BaseModel
from .types import CreateUser

class User(BaseModel):
    email: str
    first_name: str
    last_name: str

class UserRepo:
    def __init__(self):
        
    async def create(self, user: CreateUser):
        