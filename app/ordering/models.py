from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime,date

class Order(SQLModel):
    customer_id : int
    delivery_date : date


class OrderItem(SQLModel):
    order_id: int
    article_id :int

