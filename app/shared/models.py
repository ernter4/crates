import typing
from datetime import timezone, datetime
from typing import Any

from pydantic import model_serializer
from sqlmodel import SQLModel,Field

class User(SQLModel):
    username: str
    groups: list[str]

class ModelWithId(SQLModel):
    id:int


class CustomSQLModel(SQLModel):
    """
     Adds a custom serializer to serialize datetime fields with timezone info to ISO format
    """
    @model_serializer(mode="wrap",when_used="json")
    def serialize_dates_with_z(self, handler: Any) :
        # Erstmal das normale Dictionary von Pydantic/SQLModel holen
        data = handler(self)

        for key, value in data.items():
            # Prüfen, ob das Feld eine datetime ist
            if self.__class__.model_fields[key].annotation == typing.Optional[datetime] and value is not None:
                data[key] += "Z"


        return data