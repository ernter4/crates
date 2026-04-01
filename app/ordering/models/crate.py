from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from app.shared.models import ModelWithId
from app.accounting.models import Customer
if TYPE_CHECKING:
    from app.ordering.models import Order

class BaseCrate(SQLModel, table=False):
    last_seen:Optional[datetime] = None
class Crate(BaseCrate,ModelWithId,table=True):
    id: int = Field(default=None,primary_key=True)
    orders: list["Order"] = Relationship(back_populates="crate",sa_relationship_kwargs={"foreign_keys": "[Order.crate_id]"})
class CrateWithID(BaseCrate, ModelWithId):
    id: int


class CrateRecord(SQLModel):
    crate: Crate
    customer : Optional["Customer"] = None
    shapes: list[list[tuple[int,int]]] =[]
    menu_id:int = None
class CrateFilter(SQLModel):
    last_seen_gte:Optional[datetime] = None


def get_crate_filter_query(last_seen_gte:Optional[datetime] = None) -> CrateFilter:
    return CrateFilter(last_seen_gte=last_seen_gte)