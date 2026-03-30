from datetime import datetime
from typing import Generic, TypeVar, Type, Any
from sqlmodel import SQLModel, Session, select

from app.ordering.models import OrderCreate, Order, OrderWithID, OrderHistory, OrderBase
from app.shared.ModelService import ModelService, TUpdate, Tout, TCreate
from app.shared.models import User


class OrderService(ModelService[Order,OrderCreate,Order,OrderWithID]):
    def __init__(self, session: Session,current_user:User):
        super().__init__(session, Order,OrderWithID,current_user= current_user)
    def update(self, data: OrderWithID) -> OrderWithID:
        self.check_for_overlap(Order.model_validate(data))
        return super().update(data)
    def create(self, data: TCreate) -> Tout:
        self.check_for_overlap(Order.model_validate(data))
        return super().create(data)



    def check_for_overlap(self, current_order:Order):
        statement = select(Order).where(Order.crate_id == current_order.crate_id)
        if current_order.crate_id is not None:
            overlap :list[Order] = []
            if current_order.return_date is None:
                overlap_array = self.session.exec(statement.where(Order.delivery_date >= current_order.delivery_date)).all()
                for current_order in overlap_array:
                    overlap.append(current_order)
            else:
                overlap_array = self.session.exec(statement.where(
                    current_order.delivery_date > Order.delivery_date <= current_order.return_date
                    or current_order.delivery_date >= Order.return_date < current_order.return_date)).all()
                for current_order in overlap_array:
                    overlap.append(current_order)
            if len(overlap) > 0:
                error_string = "Änderung nicht möglich da eine überschneidung mit folgenden Bestellungen vorliegt:"
                for current_order in overlap:
                    error_string += f"\n{current_order.id} {current_order.delivery_date} {current_order.return_date}"
                raise ValueError(error_string)
    def create_history_entry(self,order:Order):
        entry = order.model_dump()
        entry["order_id"] = order.id
        entry["id"] = None
        entry["changed_at"] = datetime.now()
        entry["user"] = self.current_user.username
        db_entry = OrderHistory.model_validate(entry)
        self.session.add(db_entry)
        self.session.commit()
        self.session.refresh(db_entry)









