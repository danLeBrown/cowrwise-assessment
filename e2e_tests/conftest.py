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

from shared.core.database import Base, configure_engines
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
from admin_api.app.main import app as admin_app
from frontend_api.app.main import app as frontend_app

@pytest.fixture(scope="session")
def postgres_container():
    with PostgresContainer("postgres:13.3-alpine") as postgres:
        yield postgres

@pytest.fixture(scope="session")
def redis_container():
    with RedisContainer("redis:6") as redis_container:
        yield redis_container

@pytest.fixture(scope="session")
def test_db_setup(postgres_container):
    # Configure test databases according to our microservices architecture
    # Admin API uses PostgreSQL
    admin_db_url = postgres_container.get_connection_url()
    # Frontend API uses SQLite
    frontend_db_url = "sqlite:///:memory:"
    
    configure_engines(
        frontend_db_url=frontend_db_url,
        admin_db_url=admin_db_url
    )
    
    # Create tables in both databases
    Base.metadata.create_all(bind=admin_app.get_db())
    Base.metadata.create_all(bind=frontend_app.get_db())
    
    yield
    
    # Clean up
    Base.metadata.drop_all(bind=admin_app.get_db())
    Base.metadata.drop_all(bind=frontend_app.get_db())

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
def redis_service(redis_client):
    return RedisService(redis_client)

@pytest.fixture
def admin_client(test_db_setup, redis_service):
    """Admin API test client using PostgreSQL"""
    # Override dependencies
    def get_test_db():
        return admin_app.get_db()
    def get_test_redis():
        return redis_service
    admin_app.app.dependency_overrides[admin_app.get_db] = get_test_db
    admin_app.app.dependency_overrides[admin_app.get_redis] = get_test_redis
    client = TestClient(admin_app.app)
    yield client
    admin_app.app.dependency_overrides.clear()

@pytest.fixture
def frontend_client(test_db_setup, redis_service):
    """Frontend API test client using SQLite"""
    # Override dependencies
    def get_test_db():
        return frontend_app.get_db()
    def get_test_redis():
        return redis_service
    frontend_app.app.dependency_overrides[frontend_app.get_db] = get_test_db
    frontend_app.app.dependency_overrides[frontend_app.get_redis] = get_test_redis
    client = TestClient(frontend_app.app)
    yield client
    frontend_app.app.dependency_overrides.clear()
