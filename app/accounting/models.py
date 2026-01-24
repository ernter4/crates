from decimal import Decimal
from datetime import date, datetime
from typing import Optional, List
from pydantic import EmailStr, field_validator
from schwifty import IBAN, BIC

from sqlmodel import SQLModel, Field, Relationship


class BaseCustomer(SQLModel):
    first_name: str | None = None
    last_name: str | None = None
    customer_number:int
    email:  EmailStr | None = None
    sepa_mandate: bool = False
    sepa_mandate_reference: str | None = None
    sepa_mandate_date: date | None = None
    iban : IBAN | None = None
    bic : BIC | None = None
    @field_validator('sepa_mandate_reference', mode='before')
    def generate_sepa_mandate_reference(cls, v, info):
        if v is None and info.data.get('sepa_mandate' ) is True:
            return f"{info.data.get('last_name')}_{info.data.get('first_name')}"
        return v

    @field_validator('sepa_mandate_date', mode='before')
    def set_sepa_mandate_date(cls, v, info):
        if v is None and info.data.get('sepa_mandate') is True:
            return date.today()
        return v
    @field_validator('bic', mode='before')
    def generate_bic_from_iban(cls, v, info):
        if v is None and info.data.get('iban') is not None:
            iban = info.data['iban']
            return iban.bic
        return v
class Customer(BaseCustomer, table=True):
    id: int = Field(default=None, primary_key=True)
    invoices: List["Invoice"] = Relationship(back_populates="customer")
    customer_number :int
class CreateCustomer(BaseCustomer):
    customer_number: int | None = None
    sepa_mandate: bool |None = False





class BaseInvoice(SQLModel, table=False):
    customer_id: int = Field(foreign_key="customer.id",
                            sa_column_kwargs={ "name": "fk_invoice_customer"},
                             ondelete="RESTRICT",index=True)
    invoice_number: int
    billing_date: date
    amount: Decimal = Field(default=0, max_digits=5, decimal_places=3)
    exported_at : datetime | None = None


class Invoice(BaseInvoice, table=True):
    id: int = Field(default=None, primary_key=True)
    customer: "Customer" = Relationship(back_populates="invoices")
    #items: List["InvoiceItem"] = Relationship(back_populates="invoice")

class CreateInvoice(BaseInvoice):
    pass
class PublicInvoice(BaseInvoice):
    id: int



class BaseInvoiceItem(SQLModel, table=False):
    pass
    #invoice_id: int = Field(foreign_key="invoice.id" , index=True)

class InvoiceItem(BaseInvoiceItem, table=True):
    id: int | None = Field(default=None, primary_key=True)
    #invoice: "Invoice" = Relationship(back_populates="items")
class CreateInvoiceItem(BaseInvoiceItem):
    pass

class BaseAccountingExport(SQLModel, table=False):
    description: str
    start_date: date
    end_date: date

class AccountingExport(BaseAccountingExport, table=True):
    export_date: datetime
    id: int = Field(default=None, primary_key=True)
    SepaStatement: "SepaStatement" = Relationship(back_populates="export")
class CreateAccountingExport(BaseAccountingExport):
    pass



class SepaStatement(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    export_id : int = Field(foreign_key="accountingexport.id",
                            sa_column_kwargs={
                                "name": "fk_sepastatement_accountingexport"},
                            ondelete="RESTRICT", index=True)
    export : "AccountingExport" = Relationship(back_populates="SepaStatement")
    content: str
