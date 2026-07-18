from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Defaults to a local SQLite file (zero setup). For production, set DATABASE_URL
# to a PostgreSQL connection string, e.g.
#   postgresql://postgres:postgres@localhost:5432/real_estate_app
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./real_estate_app.db")

# SQLite needs check_same_thread disabled for use with the scheduler/background
# tasks that touch the DB from different threads.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    connect_args=connect_args,
    echo=os.getenv("SQL_ECHO", "False") == "True"
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
