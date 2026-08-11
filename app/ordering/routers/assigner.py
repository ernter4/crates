from fastapi import APIRouter

from app.ordering.dependencies import GreedyAssignerDep, MilpAssignerDep
from app.ordering.models import  AssignmentChanges
router =  APIRouter()


@router.post("/greedy")
def greedy_assign(assigner:GreedyAssignerDep) ->list[AssignmentChanges]:
    assigner.assign()
    return assigner.get_changes()

@router.post("/milp")
def milp_assign(assigner:MilpAssignerDep) ->list[AssignmentChanges]:
    assigner.assign()
    return assigner.get_changes()
