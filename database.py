from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from healthDB import Base
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://postgres:healthpass@localhost:5432/healthtracker"
)
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL", "postgresql://postgres:healthpass@localhost:5432/healthtracker_test"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

test_engine = create_engine(TEST_DATABASE_URL)
TestSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False)

# Only create tables manually if NOT using Alembic
if os.getenv("RUN_MIGRATIONS") != "1":
    Base.metadata.create_all(bind=engine)
    Base.metadata.create_all(bind=test_engine)


def get_db(test: bool = False):
    db = TestSessionLocal() if test else SessionLocal()
    try:
        yield db
    finally:
        db.close()
