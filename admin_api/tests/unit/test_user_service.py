import pytest
from fastapi import HTTPException
from app.domains.users.user_service import UserService
from app.domains.users.user_repo import UserRepo
from app.domains.users.user_models import User
from app.domains.users.user_schema  import CreateUserSchema

# Fixture for UserRepo
@pytest.fixture
def user_repo(db_session):
    return UserRepo(db_session)

# Fixture for UserService
@pytest.fixture
def user_service(user_repo):
    return UserService(user_repo)

def test_create_user(user_service):
    user = user_service.create(create=CreateUserSchema(email="test@example.com", first_name="John", last_name="Doe"))
    assert user.id is not None
    assert user.email == "test@example.com"

def test_create_user_duplicate_email(user_service):
    user_service.create(create=CreateUserSchema(email="test@example.com", first_name="John", last_name="Doe"))
    with pytest.raises(HTTPException):
        user_service.create(create=CreateUserSchema(email="test@example.com", first_name="Jane", last_name="Doe"))