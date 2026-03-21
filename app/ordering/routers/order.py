from datetime import date

from fastapi import APIRouter
from sqlmodel import select

from app.ordering.models import Order
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database

router = APIRouter()

@router.get("/",
            response_model=list[Order],  # ← Explizit nur Success Response definieren
            status_code=200,
            )
def get_orders(session: SessionDep,delivery_date:date = None)-> list[Order]:
    statement = select(Order)
    if delivery_date:
        statement= statement.where(Order.delivery_date == delivery_date)

    return list(session.exec(statement).all())
