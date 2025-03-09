import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.domains.users.user_models import User
from app.domains.users.user_repo import UserRepo

# Fixture for database session
@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")  # Use an in-memory SQLite database for testing
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

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