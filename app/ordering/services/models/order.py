from datetime import  datetime,time
from typing import Generic, TypeVar, Type, Any, Optional
from sqlmodel import SQLModel, Session, select, and_, or_

from app.ordering.models import OrderCreate, Order, OrderWithID, OrderHistory, OrderBase
from app.shared.ModelService import ModelService, TUpdate, Tout, TCreate
from app.shared.models import User
from app.accounting.models import Customer


class OrderService(ModelService[Order,OrderCreate,Order,OrderWithID]):
    def __init__(self, session: Session,current_user:User):
        super().__init__(session, Order,OrderWithID,current_user= current_user)
    def update(self, data: OrderWithID,item_id: Optional[int] = None) -> OrderWithID:
        self.check_for_overlap(Order.model_validate(data))

        return super().update(data,item_id)
    def create(self, data: TCreate) -> Tout:
        self.check_for_overlap(Order.model_validate(data))
        return super().create(data)



    def check_for_overlap(self, current_order:Order):

        statement = select(Order).where(Order.crate_id == current_order.crate_id).where( Order.id != current_order.id)
        overlap :list[Order]= []
        if current_order.return_date is None:
            bad_order = self.session.exec(statement.where(Order.return_date == None)).first()
            if bad_order:
                overlap.append(bad_order)
        else:
            values = self.session.exec(
                statement.where(
                    or_(
                        # Erster Block: current_order.delivery_date >= Order.delivery_date AND Order.delivery_date < Order.return_date
                        and_(
                            current_order.delivery_date <= Order.delivery_date,
                            Order.delivery_date < current_order.return_date.date()
                        ),
                        # Zweiter Block: current_order.delivery_date > Order.return_date AND Order.return_date <= current_order.return_date
                        and_(
                            datetime.combine(current_order.delivery_date,time(23,59)) < Order.return_date,
                            Order.return_date < current_order.return_date
                        )
                    )
                )
            )
            for value in values:
                overlap.append(value)

        if len(overlap)>0:
            error_message = " Überschneidung mit folgenden Bestellungen:"
            for order in overlap:
                error_message += f"\n{order.id} {order.delivery_date} {order.return_date}"
            raise ValueError(error_message)





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









