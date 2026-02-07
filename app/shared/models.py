from sqlmodel import SQLModel,Field

class User(SQLModel):
    username: str
    groups: list[str]