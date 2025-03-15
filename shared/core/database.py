from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
FRONTEND_DB_URL = os.getenv("FRONTEND_DB_URL")

fe_engine = create_engine(FRONTEND_DB_URL)
FrontendSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=fe_engine)

ADMIN_DB_URL = os.getenv("ADMIN_DB_URL")

admin_engine = create_engine(ADMIN_DB_URL)
AdminSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=admin_engine)


Base = declarative_base()