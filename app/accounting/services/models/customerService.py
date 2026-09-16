from sqlmodel import Session, select, func

from app.accounting.models import CustomerCreate, CustomerWithID, Customer
from app.shared.ModelRouter import TCreate
from app.shared.ModelService import ModelService, Tout


class CustomerService(ModelService[Customer,CustomerCreate,CustomerWithID,CustomerWithID]):
    def __init__(self, session: Session):
        super().__init__(session, Customer,CustomerWithID)
    def create(self, data: TCreate) -> Tout:
        if data.customer_number is None:
            max_number = self.session.exec(select(func.max(Customer.customer_number))).first()
            data.customer_number = (max_number or 0) + 1
        return super().create(data)
