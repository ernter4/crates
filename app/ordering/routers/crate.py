from app.ordering.models import CrateFilter, CrateWithID, get_crate_filter_query
from app.ordering.services.models.CrateService import CrateService
from fastapi import APIRouter, HTTPException, Depends

from app.shared.dependencies import SessionDep

router = APIRouter()


resource_name = "Crate"
@router.post("/",operation_id=f"{resource_name}_post")
def create(data: CrateWithID, session: SessionDep):
    return CrateService(session).create(data)

@router.get("/{item_id}", operation_id=f"{resource_name}_get_by_id")
def get( item_id: int, session: SessionDep) ->  CrateWithID:
    return CrateService(session).get(item_id)

@router.put("/{item_id}", operation_id=f"{resource_name}_put")
def update( item_id,data: CrateWithID, session: SessionDep)-> CrateWithID:
    try:
        return CrateService(session).update(data)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/",operation_id=f"{resource_name}_list")
def get_filtered( session: SessionDep , filter= Depends(get_crate_filter_query) )-> list[CrateWithID]:
    return CrateService(session).get_filtered(filter)
