from datetime import date, datetime
from typing import Optional, List

from pydantic import field_validator
from sqlmodel import SQLModel, Field, Relationship

class Customer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: Optional[ str] = Field(index=True)
    last_name: Optional[ str] = Field(index=True)
    customer_number:  int = Field(index=True, nullable=False, unique=True)
    invoices: List["Invoice"] = Relationship(back_populates="customer")

class Invoice(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    customer_id: int = Field(foreign_key="customer.id", index=True)
    customer: "Customer" = Relationship(back_populates="invoices")
    items: List["InvoiceItem"] = Relationship(back_populates="invoice")
    invoice_number: int = Field(index=True, nullable=False, unique=True)
    billing_date: Optional[date]= Field()
    amount: float = Field(nullable=False)
    status: str = Field(index=True, nullable=False)
    @field_validator('billing_date', mode='before')
    @classmethod
    def parse_billing_date(cls, value)-> date:
        if isinstance(value, str):
            return datetime.strptime(value, '%Y-%m-%d').date()

        return value

class InvoiceItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoice.id", index=True)
    invoice: "Invoice"= Relationship(back_populates="items")
