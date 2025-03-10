import pytest
from shared.models.user_models import User
from shared.repositories.user_repo import UserRepo

# Fixture for UserRepo
@pytest.fixture
def user_repo(db_session):
    return UserRepo(db_session)

def test_create_user(user_repo):
    user = User(email="test@example.com", first_name="John", last_name="Doe")
    created_user = user_repo.create(user)
    assert created_user.id is not None
    assert created_user.email == "test@example.com"

def test_find_by_email(user_repo):
    user = User(email="test@example.com", first_name="John", last_name="Doe")
    user_repo.create(user)
    found_user = user_repo.find_by_email("test@example.com")
    assert found_user is not None
    assert found_user.email == "test@example.com"