from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime,date
from app.accounting.models import Customer

class BaseCrate(SQLModel, table=False):
    last_seen:Optional[datetime] = None

class Crate(BaseCrate,table=True):
    id: int = Field(default=None,primary_key=True)
    orders: list["Order"] = Relationship(back_populates="crate")


class BaseOrder(SQLModel):
    customer_id : int =Field(foreign_key="customer.id",ondelete="RESTRICT")
    delivery_date : date
    predicted_return_date : date
    return_date : Optional[datetime]
    menu_id : int
    description:Optional[str]
    crate_id : Optional[int] =Field(foreign_key="crate.id",ondelete="RESTRICT")

class Order(BaseOrder,table=True):
    id :int = Field(default=None, primary_key=True)
    customer: "Customer" = Relationship(back_populates="orders")
    crate:Crate = Relationship(back_populates="orders")




class CrateRecord(SQLModel):
    crate: Crate
    customer : Optional[Customer] = None
    shapes: list[list[tuple[int,int]]] =[]
    menu_id:int = None





