import io
from datetime import date
from typing import Annotated

from PIL import Image

from app.ordering.services.assignment.greedy.Assigner import GreedyAssigner
from app.ordering.services.assignment.milp.Assigner import MilpAssigner

from fastapi import Depends, UploadFile

from app.shared.dependencies import SessionDep






async def get_greedy_assigner(session:SessionDep,assign_date:date):
    return GreedyAssigner(session,assign_date)
GreedyAssignerDep = Annotated[GreedyAssigner,Depends(get_greedy_assigner)]

async def get_milp_assigner(session:SessionDep,assign_date:date):
    return MilpAssigner(session,assign_date)
MilpAssignerDep = Annotated[MilpAssigner,Depends(get_milp_assigner)]


