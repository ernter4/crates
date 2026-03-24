from datetime import date,datetime



from fastapi import APIRouter
from sqlmodel import select

from app.ordering.models import Crate
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database

router = APIRouter()

@router.get("/",response_model=list[Crate])
def get_crates(session :SessionDep,seen_after:datetime= None)-> list[Crate]:
    statement = select(Crate)
    if seen_after:
        statement = statement.where(Crate.last_seen > seen_after)
    return session.exec(statement).fetchall()
@router.post("/")
def create_crate(crate :Crate, session : SessionDep):
    update_database(crate, session)
    return crate
@router.put("/{crate_id}")
def update_crate( crate_id :int, session : SessionDep):
    crate = session.get(Crate,crate_id)
    update_database(crate, session)
