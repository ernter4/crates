from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime,date

from app.accounting.models import Customer


class Order(SQLModel):
    customer_id : int
    delivery_date : date



class CrateRecord(SQLModel):
    crate_id : int
    customer : Customer = None
    shapes: list[list[tuple[int,int]]] =[]
    menu_id:int = None





