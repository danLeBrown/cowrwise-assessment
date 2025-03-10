import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from shared.core.database import Base, engine, SessionLocal

# Override the DB_URL for testing
os.environ["DB_URL"] = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def client():
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    # Drop the database tables after the test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
# Create the database tables
    Base.metadata.create_all(bind=engine)
    # Create a new database session for each test
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # Rollback any uncommitted changes
        db.close()
        # Drop the database tables after the test
        Base.metadata.drop_all(bind=engine)