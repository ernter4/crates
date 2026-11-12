from sqlmodel import Session, select, func

from app.accounting.models import CustomerCreate, CustomerWithID, Customer, CustomerFilter
from app.shared.ModelRouter import TCreate
from app.shared.ModelService import ModelService, Tout
from sqlmodel import or_


class CustomerService(ModelService[Customer, CustomerCreate, CustomerWithID, CustomerWithID]):
    def __init__(self, session: Session):
        super().__init__(session, Customer, CustomerWithID)

    def create(self, data: TCreate) -> Tout:
        if data.customer_number is None:
            max_number = self.session.exec(select(func.max(Customer.customer_number))).first()
            data.customer_number = (max_number or 0) + 1
        return super().create(data)

    def get_filtered(self, filter: CustomerFilter):
        statement = select(Customer)
        if filter.customer_number:
            statement = statement.where(Customer.customer_number == filter.customer_number)
        if filter.name:
            statement = statement.where(or_((Customer.first_name + " " + Customer.last_name).like(f"%{filter.name}%"),
                                        (Customer.last_name + " " + Customer.first_name).like(f"%{filter.name}%")))

        return self.session.exec(statement).all()
