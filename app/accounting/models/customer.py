from datetime import date
from typing import Optional, TYPE_CHECKING

from pydantic import EmailStr, field_validator
from schwifty import IBAN, BIC
from sqlmodel import SQLModel, Relationship, Field

from app.shared.models import ModelWithId, CustomSQLModel

if TYPE_CHECKING:
    from app.accounting.models import Invoice
    from app.ordering.models import Order


class BaseCustomer(SQLModel, table=False):
    first_name: str | None = None
    last_name: str | None = None
    customer_number: int
    email: EmailStr | None = None
    display_text: str | None = None
    sepa_mandate: bool = False
    sepa_mandate_reference: str | None = None
    sepa_mandate_date: date | None = None
    iban: IBAN | None = None
    bic: BIC | None = None

    @field_validator('sepa_mandate_reference', mode='before')
    def generate_sepa_mandate_reference(cls, v, info):
        if v is None and info.data.get('sepa_mandate') is True:
            return f"{info.data.get('last_name')},{info.data.get('first_name')}"
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


class Customer(BaseCustomer, ModelWithId, table=True):
    id: int = Field(default=None, primary_key=True)
    invoices: list["Invoice"] = Relationship(back_populates="customer")
    customer_number: int
    orders: list["Order"] = Relationship(back_populates="customer")


class CustomerCreate(BaseCustomer):
    customer_number: Optional[int] = None
    sepa_mandate: bool | None = False


class CustomerWithID(BaseCustomer):
    pass


class CustomerFilter(CustomSQLModel):
    customer_number: Optional[int] = None
    email: Optional[EmailStr] = None
    display_text: Optional[str] = None
    sepa_mandate: Optional[bool] = None


def get_customer_filter_query(
        customer_number: Optional[int] = None,
        email: Optional[EmailStr] = None,
        display_text: Optional[str] = None,
        sepa_mandate: Optional[bool] = None,
) -> CustomerFilter:
    return CustomerFilter(
        customer_number=customer_number,
        email=email,
        display_text=display_text,
        sepa_mandate = sepa_mandate)
