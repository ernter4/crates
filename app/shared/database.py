import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import create_engine, Session


# Engine wird EINMAL beim Import erstellt
engine = create_engine(
    os.getenv("DATABASE_URL"),
    connect_args={"check_same_thread": False},
    echo=False
)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
