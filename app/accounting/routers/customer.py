from typing import Annotated

from fastapi import Depends

from app.accounting.models import CustomerCreate, CustomerWithID, CustomerFilter, get_customer_filter_query
from app.shared.ModelRouter import BaseRouter
from app.shared.dependencies import SessionDep
from app.accounting.services.models.customerService import CustomerService

class CustomerRouter(BaseRouter[CustomerService, CustomerCreate, CustomerWithID, CustomerWithID]):
    prefix = "/customers"
    tags = ["customers"]
    dependencies = [SessionDep]

    def get_filtered(self, filter: Annotated[CustomerFilter, Depends(get_customer_filter_query)], session: SessionDep):
        return self.service_class(session).get_filtered(filter)