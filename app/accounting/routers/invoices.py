from datetime import date
from typing import List

from fastapi import APIRouter
from sqlmodel import select
from app.accounting.models import Invoice
from app.shared.database import SessionDep
router = APIRouter()
@router.get("/{invoice_id}")
def read_invoice_by_id( customer_id: int, session: SessionDep )-> Invoice| None:
    return session.get(Invoice, customer_id)
@router.get("/")
def read_invoices( billing_date_gte:date,customer_id: int,session: SessionDep) -> List[Invoice]:
    query = select(Invoice)
    if customer_id:
        query = query.where(Invoice.customer_id == customer_id)
    if billing_date_gte:
        query = query.where(Invoice.billing_date >= billing_date_gte)
    results = session.exec(query).all()
    return results
@ router.post("/")
def create_invoice( invoice: Invoice, session: SessionDep) -> Invoice:
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice
@ router.put("/{invoice_id}")
def update_invoice( invoice_id: int, updated_invoice: Invoice, session: SessionDep) -> Invoice:
    invoice = session.get(Invoice, invoice_id)
    for key, value in updated_invoice.dict(exclude_unset=True).items():
        setattr(invoice, key, value)
    session.add(invoice)
    session.commit()
    session.refresh(invoice)
    return invoice
@ router.delete("/{invoice_id}")
def delete_invoice( invoice_id: int, session: SessionDep) -> Invoice:
    invoice = session.get(Invoice, invoice_id)
    session.delete(invoice)
    session.commit()
    return invoice