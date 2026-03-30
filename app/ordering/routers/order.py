from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends


from app.ordering.models import  OrderCreate, OrderWithID, get_filter_query, OrderFilter
from app.ordering.services.models.order import OrderService
from app.shared.ModelRouter import BaseRouter
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database


class OrderRouter(BaseRouter[OrderService,OrderCreate,OrderWithID,OrderWithID]):
    prefix = "/orders"
    tags = ["orders"]
    dependencies = [SessionDep]
    def get_filtered(self,filter: Annotated[OrderFilter, Depends(get_filter_query)], session: SessionDep):
        return self.service_class(session).get_filtered(filter)