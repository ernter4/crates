from fastapi import APIRouter, FastAPI

from app.accounting.models import CustomerWithID
from app.ordering.dependencies import GreedyAssignerDep, MilpAssignerDep
from app.ordering.models import  Assignment
router =  APIRouter()


@router.post("/greedy",operation_id="greedy_assign")
def greedy_assign(assigner:GreedyAssignerDep) ->list[Assignment]:
    assigner.assign()
    return assigner.get_Assignment()
@router.get("/new_customer_cards",operation_id="get_new_customer_cards")
def get_new_customer_cards(assigner:GreedyAssignerDep)->list[CustomerWithID]:
    return assigner.get_new_customer_cards()
@router.get("/assignment",operation_id="get_assignment")
def get_assignment(assigner:GreedyAssignerDep)->list[Assignment]:
    return assigner.get_Assignment()
@router.post("/milp",operation_id="milp_assign")
def milp_assign(assigner:MilpAssignerDep) ->Assignment:
    assigner.assign()
    return assigner.get_Assignment()
