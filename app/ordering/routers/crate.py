from datetime import date,datetime



from fastapi import APIRouter
from sqlmodel import select

from app.ordering.models import Crate, CrateWithID
from app.ordering.services.models.CrateService import CrateService

from app.shared.ModelRouter import BaseRouter
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database

class CrateRouter(BaseRouter[CrateService,Crate,CrateWithID,CrateWithID]):
    prefix = "/crates"
    tags = ["crates"]
    dependencies = [SessionDep]