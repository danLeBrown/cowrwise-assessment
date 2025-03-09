import pytest
from fastapi import HTTPException
from app.domains.users.user_service import UserService
from app.domains.users.user_repo import UserRepo
from app.domains.users.user_models import User
from app.domains.users.user_schema  import CreateUser

# Fixture for UserRepo (mocked)
@pytest.fixture
def user_repo():
    class MockUserRepo:
        def __init__(self):
            self.users = []

        def create(self, user):
            user.id = 1
            self.users.append(user)
            return user

        def find_by_email(self, email):
            return next((u for u in self.users if u.email == email), None)

    return MockUserRepo()

# Fixture for UserService
@pytest.fixture
def user_service(user_repo):
    return UserService(user_repo)

def test_create_user(user_service):
    user = user_service.create(create=CreateUser(email="test@example.com", first_name="John", last_name="Doe"))
    assert user.id == 1
    assert user.email == "test@example.com"

def test_create_user_duplicate_email(user_service):
    user_service.create(create=CreateUser(email="test@example.com", first_name="John", last_name="Doe"))
    with pytest.raises(HTTPException):
        user_service.create(create=CreateUser(email="test@example.com", first_name="Jane", last_name="Doe"))