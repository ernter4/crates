import datetime
import io
import os
from datetime import date
from typing import Annotated

from PIL import Image,ImageColor
from fastapi import APIRouter, File, UploadFile

from sqlmodel import Session,select

from app.accounting.models import Customer
from app.ordering.dependencies import OcrClientDep
from app.ordering.models import Order
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database

router = APIRouter()


@router.post("/update")
def update_inventory(session:SessionDep,ocr_client: OcrClientDep):
    ocr_client.process_image()
    for record in ocr_client.records:
        statement= select(Order)
        statement = statement.where(Order.return_date is None)and(Order.customer==record.customer)and (Order.crate == record.crate)
        orders = session.exec(statement)
        if len(orders)==1:
            order = orders[0]
            order.return_date = datetime.datetime.now()
            session.add(order)
            ocr_client.draw_record(record.crate_id, ImageColor.getrgb("Green"))
    return ocr_client.get_image_response()
@router.post("/check_outgoing")
def check_outgoing(session:SessionDep,ocr_client: OcrClientDep):
    ocr_client.process_image()
    for record in ocr_client.records:
        if record.customer is not None and record.menu_id is not None:
            statement= select(Order).where(Order.crate==record.crate).where(Order.customer==record.customer).where(Order.delivery_date == date.today())
            order = session.exec(statement).first()
            if not order:
                order = Order(
                    crate = record.crate,
                    customer = record.customer,
                    delivery_date = date.today()
                )

            update_database(order,session)
            ocr_client.draw_record(record.crate.id, ImageColor.getrgb("Green"))
    return ocr_client.get_image_response()

