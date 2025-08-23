from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from healthDB import metadata

DATABASE_URL = "postgresql://healthuser:healthpass@localhost:5432/healthtracker"

engine = create_engine(DATABASE_URL, echo=True, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    metadata.create_all(bind=engine)
