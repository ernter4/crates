from fastapi import APIRouter
from sqlmodel import select

from app.ordering.models import Crate
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database

router = APIRouter()
