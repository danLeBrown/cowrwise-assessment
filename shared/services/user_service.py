from fastapi import HTTPException
from shared.schemas.user_schema import CreateUserSchema
from shared.repositories.user_repo import UserRepo
from shared.models.user_models import User
from shared.models.book_models import BorrowedBook
from redis import Redis
from sqlalchemy.orm import subqueryload

class UserService:
    def __init__(self, redis_client: Redis, user_repo: UserRepo):
        self.redis_client = redis_client
        self.user_repo = user_repo

    def create(self, create: CreateUserSchema) -> User:
        user = self.user_repo.find_by_email(create.email)
        if user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        user = self.user_repo.create(user=User(email=create.email, first_name=create.first_name, last_name=create.last_name))
        
        self.redis_client.client.publish(f"user.created", str(user.id))
        
        return user

    
    def find_all(self) -> list[User]:
        return self.user_repo.find_all()
    
    def find_all_with_borrowed_books(self) -> list[User]:
        # also expand book on the borrowed_books
        return self.user_repo.db.query(User).options(subqueryload(User.borrowed_books).subqueryload(BorrowedBook.book)).all()