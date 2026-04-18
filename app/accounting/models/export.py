from datetime import date, datetime

from sqlmodel import SQLModel, Field


class BaseAccountingExport(SQLModel, table=False):
    description: str
    start_date: date
    end_date: date

class AccountingExport(BaseAccountingExport, table=True):
    created_at: datetime
    id: int = Field(default=None, primary_key=True)
    sepa_xml: str | None = None

class CreateAccountingExport(BaseAccountingExport):
    pass


