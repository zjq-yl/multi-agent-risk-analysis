from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


DATABASE_URL = (
    f"mysql+pymysql://{settings.mysql_user}:"
    f"{settings.mysql_password}@"
    f"{settings.mysql_host}:"
    f"{settings.mysql_port}/"
    f"{settings.mysql_database}?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()