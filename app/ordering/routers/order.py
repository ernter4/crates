from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import SQLModel

from app.ordering.models import OrderCreate, OrderWithID, OrderFilter, get_order_filter_query, Order
from app.ordering.services.models.order import OrderService
from app.shared.ModelRouter import BaseRouter
from app.shared.dependencies import SessionDep, CurrentUserDep
from app.shared.update_database import update_database


router = APIRouter()


resource_name = "Order"
@router.post("/",operation_id=f"{resource_name}_post")
def create(data: OrderCreate, session: SessionDep, current_user: CurrentUserDep):
    try:
        return OrderService(session, current_user).create(data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
@router.get("/{item_id}", operation_id=f"{resource_name}_get")
def get( item_id: int, session: SessionDep, current_user: CurrentUserDep) ->  OrderWithID:
    return OrderService(session, current_user).get(item_id)

@router.put("/{item_id}", operation_id=f"{resource_name}_put")
def update( item_id:int,data: OrderWithID, session: SessionDep, current_user: CurrentUserDep)-> OrderWithID:
    try:
        return OrderService(session, current_user).update(data,item_id)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("/",operation_id=f"{resource_name}_list")
def get_filtered(  session: SessionDep,current_user: CurrentUserDep,filter = Depends(get_order_filter_query))-> list[OrderWithID]:
    return OrderService(session, current_user).get_filtered(filter)
@router.delete("/{item_id}",operation_id=f"{resource_name}_delete")
def delete(item_id:int, session: SessionDep,current_user: CurrentUserDep ):
    return OrderService(session,current_user).delete(item_id)