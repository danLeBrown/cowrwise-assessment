from fastapi import FastAPI, Depends
from app.core.database import SessionLocal
from sqlalchemy.orm import Session
from app.domains.users.user_service import UserService
from app.domains.users.user_repo import UserRepo
from alembic import command
from alembic.config import Config
from app.domains.users.user_schema import User, CreateUser

app = FastAPI()

def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")


# Call this function at startup
run_migrations()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/users", response_model=list[User])
async def get_users(db: Session = Depends(get_db)):
    user_service = UserService(user_repo=UserRepo(db))
    return user_service.find_all()


@app.post("/users", response_model=User)
async def create_user(user: CreateUser, db: Session = Depends(get_db)):
    user_service = UserService(user_repo=UserRepo(db))
    return user_service.create(user)
