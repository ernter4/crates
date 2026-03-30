from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from app.shared.models import ModelWithId

if TYPE_CHECKING:
    from app.ordering.models import Order,Customer

class BaseCrate(SQLModel, table=False):
    last_seen:Optional[datetime] = None
class Crate(BaseCrate,ModelWithId,table=True):
    id: int = Field(default=None,primary_key=True)
    orders: list["Order"] = Relationship(back_populates="crate",sa_relationship_kwargs={"foreign_keys": "[Order.crate_id]"})

class CrateWithID(BaseCrate, ModelWithId):
    id: int
    model_config = {
        "json_schema_extra": {"title": "Crate"}
    }


class CrateRecord(SQLModel):
    crate: Crate
    customer : Optional["Customer"] = None
    shapes: list[list[tuple[int,int]]] =[]
    menu_id:int = None
