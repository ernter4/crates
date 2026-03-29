import base64
import datetime
import io
import os
from datetime import date
from io import BytesIO
from typing import Annotated, Optional

from PIL import Image, ImageColor
from fastapi import APIRouter, File, UploadFile
from fastapi import Response

from sqlmodel import Session, select
from starlette.responses import HTMLResponse

from app.accounting.models import Customer
from app.ordering.dependencies import OcrClientDep
from app.ordering.models import Order, ImageResponse
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database

router = APIRouter()


@router.post("/update")
def update_inventory(session: SessionDep, ocr_client: OcrClientDep)-> ImageResponse:
    ocr_client.process_image()
    for record in ocr_client.records:

        statement = select(Order)
        statement = statement.where(Order.crate == record.crate).where(Order.customer == record.customer).where(Order.menu_id == record.menu_id)
        # open order
        open_order:Optional[Order] = session.exec(statement.where(Order.return_date is None)).first()
        last_order:Optional[Order]  = session.exec(select(Order).where(Order.crate==record.crate).order_by(Order.return_date)).first()
        if open_order :
            open_order.return_date = datetime.datetime.now()
            update_database(open_order, session)
            record.crate.last_seen = datetime.datetime.now()
            update_database(record.crate, session)
            ocr_client.draw_record(record.crate.id, ImageColor.getrgb("Green"))
        elif last_order.customer == record.customer and last_order.menu_id == record.menu_id:
            record.crate.last_seen = datetime.datetime.now()
            update_database(record.crate, session)
            ocr_client.draw_record(record.crate.id, ImageColor.getrgb("Green"))
    buffer = BytesIO()
    ocr_client.image.save(buffer, format='JPEG', quality=90)
    # Zu Base64 encodieren
    base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return ImageResponse(image=base64_str)


@router.post("/check_outgoing")
def check_outgoing(delivery_date: date, session: SessionDep, ocr_client: OcrClientDep)-> ImageResponse:
    ocr_client.process_image()
    for record in ocr_client.records:
        old_order = session.exec(select(Order).where(Order.crate == record.crate).where(Order.return_date is None)).first()
        if old_order is not None and (old_order.delivery_date != delivery_date or old_order.menu_id != record.menu_id or old_order.customer != record.customer):
            old_order.return_date = datetime.datetime.now()
            update_database(old_order, session)

        if record.customer is not None and record.menu_id is not None:
            statement = select(Order).where(Order.crate == record.crate).where(Order.customer == record.customer).where(
                Order.delivery_date == delivery_date)
            order = session.exec(statement).first()
            if not order:
                order = Order(
                    crate=record.crate,
                    customer=record.customer,
                    delivery_date=delivery_date,
                    menu_id=record.menu_id
                )

            update_database(order, session)
            ocr_client.draw_record(record.crate.id, ImageColor.getrgb("Green"))
    buffer = BytesIO()
    ocr_client.image.save(buffer, format='JPEG', quality=90)
    # Zu Base64 encodieren
    base64_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return ImageResponse(image=base64_str)