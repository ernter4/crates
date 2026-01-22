from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import  select
from fastapi import APIRouter
from app.accounting.models import Customer
from app.shared.database import SessionDep

router = APIRouter()
@router.post("/")
def create_customer(customer: Customer, session: SessionDep) -> Customer:
    if customer.customer_number is None:

        max_number = session.exec(select(func.max(Customer.customer_number))).first()
        customer.customer_number = (max_number or 0) + 1
    try:
        session.add(customer)
        session.commit()
        session.refresh(customer)
    except Exception:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Customer could not be created. ")
    return customer
@router.get("/")
def read_customers(session: SessionDep) -> list[Customer]:
    customers = session.exec(select(Customer)).all()
    return customers
@router.get("/{customer_id}")
def read_customer_by_id(customer_id: int, session: SessionDep) -> Customer:
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with id {customer_id} not found.")
    return customer
@router.put("/{customer_id}")
def update_customer(customer_id: int, updated_customer: Customer, session: SessionDep) -> Customer:
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with id {customer_id} not found.")
    for key, value in updated_customer.dict(exclude_unset=True).items():
        setattr(customer, key, value)
    try:
        session.add(customer)
        session.commit()
        session.refresh(customer)
    except Exception:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"Customer could not be updated. ")
    return customer
@router.delete("/{customer_id}")
def delete_customer(customer_id: int, session: SessionDep) -> Customer:
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer with id {customer_id} not found.")
    session.delete(customer)
    session.commit()
    return customer