from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from ..config.settings import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

connect_kwargs = {}
if "postgresql" in SQLALCHEMY_DATABASE_URL.lower():
    connect_kwargs["connect_args"] = {
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=180,
    pool_pre_ping=True,
    **connect_kwargs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()