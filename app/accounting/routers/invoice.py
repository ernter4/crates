from datetime import date
from fastapi import HTTPException
from typing import List

from fastapi import APIRouter
from sqlmodel import select
from app.accounting.models import Invoice, BaseInvoice
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database, delete_from_database

router = APIRouter()
