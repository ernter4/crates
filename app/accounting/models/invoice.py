from datetime import date, datetime
from decimal import Decimal
from typing import Annotated

from sqlmodel import Field, Relationship, SQLModel

from app.accounting.models import Customer

# app/shared/types.py
import decimal
from typing import Any
from pydantic import BaseModel
class DecimalAsString(decimal.Decimal):

    @classmethod
    def __get_pydantic_core_schema__(cls, source, handler):
        # Delegate core schema generation to the builtin decimal.Decimal handler
        # Use handler.generate_schema to avoid infinite recursion
        return handler.generate_schema(decimal.Decimal)
    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: Any, handler: Any):
        return {"type": "string", "format": "number"}
class BaseInvoice(SQLModel, table=False):
    customer_id: int = Field(foreign_key="customer.id",
                            sa_column_kwargs={ "name": "fk_invoice_customer"},
                             ondelete="RESTRICT",index=True)
    invoice_number: int
    billing_date: date
    amount:DecimalAsString  = Field(default=0, max_digits=8, decimal_places=2)
    exported_at : datetime | None = None


class Invoice(BaseInvoice, table=True):
    id: int = Field(default=None, primary_key=True)
    customer: "Customer" = Relationship(back_populates="invoices")
    items: list["InvoiceItem"] = Relationship(back_populates="invoice")

class CreateInvoice(BaseInvoice):
    pass
class PublicInvoice(BaseInvoice):
    id: int



class BaseInvoiceItem(SQLModel, table=False):
   invoice_id: int = Field(foreign_key="invoice.id" , index=True)

class InvoiceItem(BaseInvoiceItem, table=True):
    id: int | None = Field(default=None, primary_key=True)
    invoice: "Invoice" = Relationship(back_populates="items")
class CreateInvoiceItem(BaseInvoiceItem):
    pass