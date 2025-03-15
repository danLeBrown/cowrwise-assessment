from fastapi import HTTPException
from shared.schemas.user_schema import CreateUserSchema
from shared.repositories.user_repo import UserRepo
from shared.models.user_models import User
from redis import Redis
class UserService:
    def __init__(self, user_repo: UserRepo):
        self.user_repo = user_repo

    def create(self, create: CreateUserSchema) -> User:
        user = self.user_repo.find_by_email(create.email)
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        return self.user_repo.create(user=User(email=create.email, first_name=create.first_name, last_name=create.last_name))
    
    def find_all(self) -> list[User]:
        return self.user_repo.find_all()