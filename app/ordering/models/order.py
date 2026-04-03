from datetime import date, datetime
from typing import Optional, TYPE_CHECKING

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
    menu_id : int
    description:Optional[str] =None
    crate_id : Optional[int] =Field(foreign_key="crate.id",ondelete="RESTRICT")

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
    delivery_date:Optional[date] = None
    return_date_exists:Optional[bool] = None
    delivery_date_gte:Optional[date] = None
    delivery_date_lte:Optional[date] = None

def get_order_filter_query(
    customer_id: Optional[int] = None,
    crate_id: Optional[int] = None,
    delivery_date: Optional[date] = None,
    return_date_exists: Optional[bool] = None,
    delivery_date_gte: Optional[date] = None,
    delivery_date_lte: Optional[date] = None

) -> OrderFilter:
    return OrderFilter(
        customer_id=customer_id,
        crate_id=crate_id,
        delivery_date=delivery_date,
        delivery_date_gte = delivery_date_gte,
        delivery_date_lte = delivery_date_lte,
        return_date_exists=return_date_exists
    )

class AssignmentChanges(SQLModel):
    order: Order
    old_customer: "Customer"
