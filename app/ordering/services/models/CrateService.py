from datetime import datetime
from typing import Optional

from sentry_sdk import session
from sqlmodel import Session, select

from app.ordering.models import CrateWithID, Crate, Order, OrderWithID
from app.ordering.services.models.order import OrderService
from app.shared.ModelService import ModelService, TUpdate, Tout


class CrateService(ModelService[Crate,Crate,CrateWithID,CrateWithID]):
    def __init__(self, session: Session):
        super().__init__(session, Crate,CrateWithID)
    def update(self, data: TUpdate,item_id:Optional[int]= None ) -> CrateWithID:

        statement = select(Order).where(Order.return_date == None)
        if item_id:
            statement = statement.where(Order.crate_id == item_id)
        else:
            statement = statement.where(Order.crate_id == data.id)
        order:OrderWithID = self.session.exec(statement).first()
        if order:
            order.return_date = datetime.now()
            OrderService(self.session,self.current_user).update(order)

        return super().update(data,item_id)