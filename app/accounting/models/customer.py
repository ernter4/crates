from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship

from app.accounting.models.invoice import Invoice


class Customer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: Optional[ str] = Field(index=True)
    last_name: Optional[ str] = Field(index=True)
    customer_number:  int = Field(index=True, nullable=False, unique=True)
    invoices: List["Invoice"] = Relationship(back_populates="customer")
