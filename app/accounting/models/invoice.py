from datetime import date
from typing import List

from sqlmodel import SQLModel, Field, Relationship


class InvoiceBase(SQLModel):
    customer_id: int = Field(foreign_key="customer.id", index=True)
    customer: "Customer" = Relationship(back_populates="invoices")
    items: List["InvoiceItem"] = Relationship(back_populates="invoice")
    invoice_number: int = Field(index=True, nullable=False, unique=True)
    billing_date: date= Field()
    amount: float = Field(nullable=False)
class Invoice(InvoiceBase, table=True):
    id: int = Field(default=None, primary_key=True)


class InvoiceCreate(InvoiceBase, table=False):
    pass

class InvoicePublic(InvoiceBase, table=False):
    id: int



class InvoiceItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    invoice_id: int = Field(foreign_key="invoice.id", index=True)
    invoice: "Invoice"= Relationship(back_populates="items")
