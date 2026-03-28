from datetime import date

from fastapi import APIRouter
from sqlmodel import select

from app.ordering.models import Order, BaseOrder, CreateOrder, OutputOrder
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database

router = APIRouter()

@router.get("/")
def get_orders(session: SessionDep,delivery_date:date = None)-> list[OutputOrder]:
    statement = select(Order)
    if delivery_date:
        statement= statement.where(Order.delivery_date == delivery_date)

    return list(session.exec(statement).all())
@router.get("/{order_id}", response_model=OutputOrder)
def get_order_by_id(order_id: int, session: SessionDep):
    return session.get(Order, order_id)

@router.post("/")
def create_order(order: CreateOrder, session: SessionDep):
    db_order = Order.model_validate(order)
    update_database(db_order, session)
    return order

@router.put("/{order_id}")
def update_order(order_id: int, updated_order: OutputOrder, session: SessionDep):
    order = session.get(Order, order_id)
    for key, value in updated_order.model_dump(exclude_unset=True).items():
        setattr(order, key, value)

    update_database(order, session)
