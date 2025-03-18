import os
import pytest
import redis
from sqlalchemy import create_engine
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker
from testcontainers.redis import RedisContainer

from admin_api.app.main import app as admin_app
from frontend_api.app.main import app as frontend_app
from shared.core.database import Base
from shared.utils.redis_service import RedisService

# @pytest.fixture(scope="session")
# def postgres_container():
#     postgres = PostgresContainer("postgres:13-alpine")
#     postgres.start()
#     return postgres

@pytest.fixture(scope="session")
def redis_container():
    redis_container = RedisContainer("redis:6-alpine")
    redis_container.start()
    print(redis_container)
    return redis_container

@pytest.fixture(scope="session")
def admin_db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="session")
def frontend_db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

@pytest.fixture(scope="function")
def admin_db_session(admin_db_engine):
    SessionLocal = sessionmaker(bind=admin_db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="function")
def frontend_db_session(frontend_db_engine):
    SessionLocal = sessionmaker(bind=frontend_db_engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

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

@pytest.fixture(scope="function")
def admin_client(admin_db_session, redis_service):
    # Override dependencies
    admin_app.app.dependency_overrides[admin_app.get_db] = lambda: admin_db_session
    admin_app.app.dependency_overrides[admin_app.get_redis] = lambda: redis_service
    
    client = TestClient(admin_app.app)
    yield client
    admin_app.app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def frontend_client(frontend_db_session, redis_service):
    # Override dependencies
    frontend_app.app.dependency_overrides[frontend_app.get_db] = lambda: frontend_db_session
    frontend_app.app.dependency_overrides[frontend_app.get_redis] = lambda: redis_service
    
    client = TestClient(frontend_app.app)
    yield client
    frontend_app.app.dependency_overrides.clear()