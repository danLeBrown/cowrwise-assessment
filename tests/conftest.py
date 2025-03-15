import os
import pytest
from fastapi.testclient import TestClient
import admin_api.app.main as admin_app
import frontend_api.app.main as frontend_app
from shared.core.database import Base, admin_engine, frontend_engine, SessionLocal
from testcontainers.redis import RedisContainer

redis = RedisContainer("redis:5.0.3-alpine")
print(redis.port)

# Override the DB_URL for testing
os.environ["DB_URL"] = "sqlite:///:memory:"
os.environ["FRONTEND_DB_URL"] = "sqlite:///:memory:"
os.environ["ADMIN_DB_URL"] = "sqlite:///:memory:"
print(os.getenv("DB_URL"), os.getenv("FRONTEND_DB_URL"), os.getenv("ADMIN_DB_URL"))


@pytest.fixture(scope="module")
def frontend_client():
    # Create the database tables
    Base.metadata.create_all(bind=frontend_engine)
    yield TestClient(frontend_app.app)
    # Drop the database tables after the test
    Base.metadata.drop_all(bind=frontend_engine)

@pytest.fixture(scope="module")
def admin_client():
    # Create the database tables
    Base.metadata.create_all(bind=admin_engine)
    yield TestClient(admin_app.app)
    # Drop the database tables after the test
    Base.metadata.drop_all(bind=admin_engine)
    

# @pytest.fixture(scope="function")
# def db_session():
# # Create the database tables
#     Base.metadata.create_all(bind=engine)
#     # Create a new database session for each test
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.rollback()  # Rollback any uncommitted changes
#         db.close()
#         # Drop the database tables after the test
#         Base.metadata.drop_all(bind=engine)