from contextlib import contextmanager

import app.models
from app.core.config import settings
from sqlmodel import Session, SQLModel, create_engine

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def create_tables() -> None:
    SQLModel.metadata.create_all(engine)


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session
