from datetime import date, datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import text
from sqlmodel import Field, Relationship, SQLModel

from app.shared.models import CustomSQLModel, ModelWithId
from app.accounting.models import Customer
if TYPE_CHECKING:
    from app.ordering.models import Crate


class OrderBase(CustomSQLModel):
    customer_id : int =Field(foreign_key="customer.id",ondelete="RESTRICT")
    delivery_date : date
    predicted_return_date : Optional[date] = None
    return_date : Optional[datetime] = None
    assigned_crate_id : Optional[int] =Field(foreign_key="crate.id",ondelete="RESTRICT")
    last_changed:Optional[datetime] = datetime.now()
    menu_id : int
    description:Optional[str] =None
    crate_id : Optional[int] =Field(foreign_key="crate.id",ondelete="RESTRICT")
    deleted: bool = Field(
        default=False,
        sa_column_kwargs={"server_default": text("false")}
    )

class Order(OrderBase, ModelWithId, table=True):
    id :Optional [int] = Field(default=None, primary_key=True)
    customer: "Customer" = Relationship(back_populates="orders")
    crate:"Crate" = Relationship(back_populates="orders",sa_relationship_kwargs={"foreign_keys": "[Order.crate_id]"})
    assigned_crate:"Crate" = Relationship(sa_relationship_kwargs={"foreign_keys": "[Order.assigned_crate_id]"})
class OrderCreate(OrderBase):
    id:Optional[int] = None
    assigned_crate_id:Optional[int] = None
class OrderWithID(OrderBase, ModelWithId):
    id: int
    model_config = {
        "json_schema_extra": {"title": "Order"}
    }


class OrderHistory(OrderBase,table=True):
    id :Optional [int] = Field(default=None, primary_key=True)
    changed_by:str
    changed_at:datetime
    order_id:int = Field(foreign_key="order.id",ondelete="RESTRICT")










class OrderFilter(CustomSQLModel):
    customer_id:Optional[int] = None
    crate_id:Optional[int] = None
    crate_id_exists:Optional[bool] = None
    delivery_date:Optional[date] = None
    return_date_exists:Optional[bool] = None
    delivery_date_gte:Optional[date] = None
    delivery_date_lte:Optional[date] = None
    deleted:Optional[bool] = None
    menu_id:Optional[int] = None

def get_order_filter_query(
    customer_id: Optional[int] = None,
    crate_id: Optional[int] = None,
    crate_id_exists: Optional[bool] = None,
    delivery_date: Optional[date] = None,
    return_date_exists: Optional[bool] = None,
    delivery_date_gte: Optional[date] = None,
    delivery_date_lte: Optional[date] = None,
    menu_id: Optional[int] = None,
deleted:Optional[bool] = None
) -> OrderFilter:
    return OrderFilter(
        customer_id=customer_id,
        crate_id=crate_id,
        delivery_date=delivery_date,
        delivery_date_gte = delivery_date_gte,
        delivery_date_lte = delivery_date_lte,
        return_date_exists=return_date_exists,
        deleted= deleted,
        crate_id_exists=crate_id_exists,
        menu_id=menu_id
    )

class AssignmentChanges(SQLModel):
    order: Order
    old_customer: "Customer"


class WeeklyOrderCreate(SQLModel):
    customer_id: int
    date: date

    monday: list[int] = Field(default_factory=list)
    tuesday: list[int] = Field(default_factory=list)
    wednesday: list[int] = Field(default_factory=list)
    thursday: list[int] = Field(default_factory=list)
    friday: list[int] = Field(default_factory=list)
    saturday: list[int] = Field(default_factory=list)
    sunday: list[int] = Field(default_factory=list)
