from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime,date
from app.accounting.models import Customer
from app.shared.models import ModelWithId, CustomSQLModel


class BaseCrate(SQLModel, table=False):
    last_seen:Optional[datetime] = None
    id: int
class Crate(BaseCrate,table=True):
    id: int = Field(default=None,primary_key=True)
    orders: list["Order"] = Relationship(back_populates="crate",sa_relationship_kwargs={"foreign_keys": "[Order.crate_id]"})


class BaseOrder(CustomSQLModel):
    customer_id : int =Field(foreign_key="customer.id",ondelete="RESTRICT")
    delivery_date : date = None
    predicted_return_date : Optional[date] = None
    return_date : Optional[datetime] = None
    assigned_crate_id : Optional[int] =Field(foreign_key="crate.id",ondelete="RESTRICT")
    menu_id : int
    description:Optional[str] =None
    crate_id : Optional[int] =Field(foreign_key="crate.id",ondelete="RESTRICT")

class Order(BaseOrder,ModelWithId,table=True):
    id :Optional [int] = Field(default=None, primary_key=True)
    customer: "Customer" = Relationship(back_populates="orders")
    crate:Crate = Relationship(back_populates="orders",sa_relationship_kwargs={"foreign_keys": "[Order.crate_id]"})
    assigned_crate:Crate = Relationship(sa_relationship_kwargs={"foreign_keys": "[Order.assigned_crate_id]"})
class CreateOrder(BaseOrder):
    id:Optional[int] = None
class OutputOrder(BaseOrder):
    id:int


class CrateRecord(SQLModel):
    crate: Crate
    customer : Optional[Customer] = None
    shapes: list[list[tuple[int,int]]] =[]
    menu_id:int = None

class AssignmentChanges(SQLModel):
    order: Order
    old_customer: Customer



class ImageResponse(SQLModel):
    image:str




