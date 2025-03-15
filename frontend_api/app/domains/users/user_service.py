from fastapi import HTTPException
from shared.schemas.user_schema import CreateUserSchema
from shared.repositories.user_repo import UserRepo
from shared.models.user_models import User
from redis import Redis
import json

class UserService:
    def __init__(self, redis_client: Redis, user_repo: UserRepo):
        self.redis_client = redis_client
        self.user_repo = user_repo

    def create(self, create: CreateUserSchema) -> User:
        user = self.user_repo.find_by_email(create.email)
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user = self.user_repo.create(user=User(email=create.email, first_name=create.first_name, last_name=create.last_name))
        
        self.redis_client.publish(f"user.created", str(user.id))
        
        return user
    
    def find_all(self) -> list[User]:
        return self.user_repo.find_all()