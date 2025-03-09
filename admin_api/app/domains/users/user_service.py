from fastapi import HTTPException
from app.domains.users.user_schema import CreateUserSchema
from app.domains.users.user_repo import UserRepo
from app.domains.users.user_models import User

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