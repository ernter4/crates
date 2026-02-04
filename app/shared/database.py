import os

from sqlalchemy import text
from sqlmodel import create_engine, Session

# Engine wird EINMAL beim Import erstellt
engine = create_engine(
    os.getenv("CRATES_DATABASE_URL"),
    connect_args={"check_same_thread": False,
                  },
    echo=False
)


def get_session():
    with Session(engine) as session:
        session.exec(text("PRAGMA foreign_keys=ON"))
        yield session



