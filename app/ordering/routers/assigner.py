from fastapi import APIRouter

from app.ordering.dependencies import GreedyAssignerDep
from app.ordering.models import  AssignmentChanges
router =  APIRouter()


@router.post("/greedy")
def greedy_assign(assigner:GreedyAssignerDep) ->list[AssignmentChanges]:
    assigner.assign()
    return assigner.get_changes()
