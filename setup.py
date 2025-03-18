from setuptools import setup, find_packages

setup(
    name="library-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.115.11",
        "uvicorn==0.34.0",
        "sqlalchemy==2.0.38",
        "pydantic==2.10.6",
        "redis==5.2.1",
        "pytest==8.3.5",
        "pytest-asyncio==0.25.3",
        "httpx==0.28.1",
        "testcontainers==4.9.2",
        "alembic==1.15.1",
        "psycopg2-binary==2.9.10",
        "python-dotenv==1.0.1"
    ],
)
