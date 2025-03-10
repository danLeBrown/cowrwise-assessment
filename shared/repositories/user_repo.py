from sqlalchemy.orm import Session
from shared.models.user_models import User

class UserRepo:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return  user

    def find_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def find_all(self) -> list[User]:
        return self.db.query(User).all()