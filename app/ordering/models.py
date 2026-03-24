from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime,date
from app.accounting.models import Customer

class BaseCrate(SQLModel, table=False):
    last_seen:Optional[datetime] = None
    id: int
class Crate(BaseCrate,table=True):
    id: int = Field(default=None,primary_key=True)
    orders: list["Order"] = Relationship(back_populates="crate")


class BaseOrder(SQLModel):
    customer_id : int =Field(foreign_key="customer.id",ondelete="RESTRICT")
    delivery_date : date = None
    predicted_return_date : Optional[date] = None
    return_date : Optional[datetime] = None
    menu_id : int
    description:Optional[str] =None
    crate_id : Optional[int] =Field(foreign_key="crate.id",ondelete="RESTRICT")

class Order(BaseOrder,table=True):
    id :Optional [int] = Field(default=None, primary_key=True)
    customer: "Customer" = Relationship(back_populates="orders")
    crate:Crate = Relationship(back_populates="orders")
class CreateOrder(BaseOrder):
    id:Optional[int] = None



class CrateRecord(SQLModel):
    crate: Crate
    customer : Optional[Customer] = None
    shapes: list[list[tuple[int,int]]] =[]
    menu_id:int = None

class ImageResponse(SQLModel):
    image:str




