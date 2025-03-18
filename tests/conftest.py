import pytest
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer
from fastapi.testclient import TestClient
import redis

from shared.core.database import Base
from shared.utils.redis_service import RedisService
import sys
import os

# Add service paths to Python path for our microservices architecture
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
frontend_path = os.path.join(project_root, 'frontend_api')
admin_path = os.path.join(project_root, 'admin_api')
shared_path = os.path.join(project_root, 'shared')

# Ensure proper import order: shared first, then services
for path in [shared_path, admin_path, frontend_path, project_root]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Import service modules
import admin_api.app.main as admin_app
import frontend_api.app.main as frontend_app

# Allow overriding database engines for testing
frontend_engine = None
admin_engine = None

@pytest.fixture(scope="session")
def admin_postgres_container():
    with PostgresContainer("postgres:13.3-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def frontend_postgres_container():
    with PostgresContainer("postgres:13.3-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:6") as redis_container:
        yield redis_container

@pytest.fixture(scope="session")
def test_db_setup(admin_postgres_container, frontend_postgres_container):
    # Configure test databases according to our microservices architecture
    # Admin API uses PostgreSQL
    admin_db_url = admin_postgres_container.get_connection_url()
    # Frontend API uses PostgreSQL
    """
    I couldn't use SQLite here because, sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 6189133824 and this is thread id 8627058752.
    """
    frontend_db_url = frontend_postgres_container.get_connection_url()
    
    os.environ["FRONTEND_DB_URL"] = frontend_db_url
    os.environ["ADMIN_DB_URL"] = admin_db_url
    
    global frontend_engine, admin_engine

    frontend_engine = create_engine(frontend_db_url)
    admin_engine = create_engine(admin_db_url)
    
    # Create tables in both databases
    Base.metadata.create_all(bind=admin_engine)
    Base.metadata.create_all(bind=frontend_engine)
    
    yield
    
    # Clean up
    Base.metadata.drop_all(bind=admin_engine)
    Base.metadata.drop_all(bind=frontend_engine)

@pytest.fixture(scope="function")
def redis_client(redis_container):
    client = redis.Redis(
        host=redis_container.get_container_host_ip(),
        port=redis_container.get_exposed_port(6379),
        decode_responses=True
    )
    yield client
    client.flushall()

@pytest.fixture(scope="function")
def get_admin_db(test_db_setup):
    db = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)()
    print('admin_engine', admin_engine)
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def get_frontend_db(test_db_setup):
    db = sessionmaker(autocommit=False, autoflush=False, bind=frontend_engine)()
    print('frontend_engine', frontend_engine)
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def redis_service(redis_client):
    return RedisService(redis_client)


@pytest.fixture(scope="function", autouse=True)
def admin_client(get_admin_db, get_frontend_db, redis_service):
    """Admin API test client using PostgreSQL"""
    
    def get_test_admin_db():
        return get_admin_db

    def get_test_frontend_db():
        return get_frontend_db
    
    def get_test_redis():
        return redis_service

    admin_app.app.dependency_overrides[admin_app.get_admin_db] = get_test_admin_db
    admin_app.app.dependency_overrides[admin_app.get_frontend_db] = get_test_frontend_db
    admin_app.app.dependency_overrides[admin_app.get_redis] = get_test_redis
    client = TestClient(admin_app.app)
    yield client
    admin_app.app.dependency_overrides.clear()
    
@pytest.fixture(scope="function", autouse=True)
def frontend_client(test_db_setup, get_admin_db, get_frontend_db, redis_service):
    """Frontend API test client using SQLite"""
    # # Override dependencies
    def get_test_admin_db():
        return get_admin_db

    def get_test_frontend_db():
        return get_frontend_db
    
    def get_test_redis():
        return redis_service

    frontend_app.app.dependency_overrides[frontend_app.get_admin_db] = get_test_admin_db
    frontend_app.app.dependency_overrides[frontend_app.get_frontend_db] = get_test_frontend_db
    frontend_app.app.dependency_overrides[frontend_app.get_redis] = get_test_redis
    client = TestClient(frontend_app.app)
    yield client
    frontend_app.app.dependency_overrides.clear()
