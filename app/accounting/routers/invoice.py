from datetime import date
from fastapi import HTTPException
from typing import List

from fastapi import APIRouter
from sqlmodel import select
from app.accounting.models import Invoice, BaseInvoice
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database, delete_from_database

router = APIRouter()

@ router.post("/")
def create_invoice( invoice: BaseInvoice, session: SessionDep) -> Invoice:
    invoice_db = Invoice.model_validate(invoice)
    return update_database(invoice_db, session)

@router.get("/{invoice_id}")
def read_invoice_by_id( customer_id: int, session: SessionDep )-> Invoice| None:
    return session.get(Invoice, customer_id)
@router.get("/")
def read_invoices(session: SessionDep, billing_date_gte:date = None,customer_id: int = None) -> List[Invoice]:
    query = select(Invoice)
    if customer_id:
        query = query.where(Invoice.customer_id == customer_id)
    if billing_date_gte:
        query = query.where(Invoice.billing_date >= billing_date_gte)
    results = session.exec(query).all()
    return results

@ router.put("/{invoice_id}")
def update_invoice( invoice_id: int, updated_invoice: Invoice, session: SessionDep) -> Invoice:
    invoice = session.get(Invoice, invoice_id)
    for key, value in updated_invoice.model_dump(exclude_unset=True).items():
        setattr(invoice, key, value)
    return update_database(invoice, session)
@ router.delete("/{invoice_id}")
def delete_invoice( invoice_id: int, session: SessionDep) -> dict:
    invoice = session.get(Invoice, invoice_id)
    return delete_from_database(invoice, session)


