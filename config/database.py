from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config.config import settings

engine = create_engine(settings.NEON_DB_STRING.replace("postgresql://", "postgresql+psycopg://"))
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
