from app.core.config import settings
from sqlmodel import Session, create_engine


connect_args = {"check_same_thread": False}
engine = create_engine(url=settings.DATABASE_URL, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session
