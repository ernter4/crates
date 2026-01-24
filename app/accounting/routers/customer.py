import logging

from fastapi import HTTPException
from sqlalchemy import func
from sqlmodel import  select
from fastapi import APIRouter
from app.accounting.models import Customer, BaseCustomer, CreateCustomer
from app.shared.update_database import update_database, delete_from_database
from app.shared.dependencies import SessionDep
logger = logging.getLogger(__name__)
router = APIRouter()
@router.post("/")
def create_customer(customer: CreateCustomer, session: SessionDep) -> Customer:
    if customer.customer_number is None:
        max_number = session.exec(select(func.max(Customer.customer_number))).first()
        customer.customer_number = (max_number or 0) + 1
    customer_db = Customer.model_validate(customer)
    return update_database(customer_db,session)
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
    for key, value in updated_customer.model_dump(exclude_unset=True).items():
        setattr(customer, key, value)
    return update_database(customer, session)
@router.delete("/{customer_id}")
def delete_customer(customer_id: int, session: SessionDep) -> Customer:
    customer = session.get(Customer, customer_id)
    return delete_from_database(customer, session)
