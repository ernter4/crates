from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.shared.models import ModelWithId

if TYPE_CHECKING:
    from app.accounting.models import Customer


class BaseInvoice(SQLModel, table=False):
    customer_id: int = Field(foreign_key="customer.id",
                            sa_column_kwargs={ "name": "fk_invoice_customer"},
                             ondelete="RESTRICT",index=True)
    invoice_number: int
    billing_date: date
    exported_at: datetime | None = None


class Invoice(BaseInvoice, ModelWithId, table=True):
    id: int = Field(default=None, primary_key=True)
    customer: "Customer" = Relationship(back_populates="invoices")
    items: list["InvoiceItem"] = Relationship(back_populates="invoice")


class InvoiceWithID(BaseInvoice, ModelWithId):
    id: int


class BaseInvoiceItem(SQLModel, table=False):
    id: int = Field(foreign_key="invoice.id" , index=True)
    article_id: int = Field(foreign_key="article.id", index=True)
    price: int
    service_date_start: date
    service_date_end: Optional[date]
    tax_rate_id: int = Field(foreign_key="tax_rate.id", index=True)
class InvoiceItem(BaseInvoiceItem, ModelWithId, table=True):
    id: int | None = Field(default=None, primary_key=True)
    invoice: "Invoice" = Relationship(back_populates="items")#

class InvoiceItemWithID(BaseInvoiceItem, ModelWithId):
    id: int


