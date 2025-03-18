from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Default database URLs for development
FRONTEND_DB_URL = os.getenv("FRONTEND_DB_URL", "sqlite:///./frontend.db")
ADMIN_DB_URL = os.getenv("ADMIN_DB_URL", "sqlite:///./admin.db")

# def configure_engines(frontend_db_url=None, admin_db_url=None):
#     """Configure database engines. Used primarily for testing."""
#     global frontend_engine, admin_engine
frontend_engine = create_engine(FRONTEND_DB_URL)
admin_engine = create_engine(ADMIN_DB_URL)

# Create session factories
def get_frontend_session():
    return sessionmaker(autocommit=False, autoflush=False, bind=frontend_engine)()

def get_admin_session():
    return sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)()

Base = declarative_base()