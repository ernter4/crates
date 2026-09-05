
from datetime import timedelta,datetime,time
from os import waitid_result

from sqlmodel import select, exists, func, desc, and_, or_
from typing import cast
from sqlalchemy.orm import aliased

from app.accounting.models import Customer
from app.ordering.models import Order, Crate
from app.ordering.services.assignment.interface import AssignmentServiceInterface


class GreedyAssigner(AssignmentServiceInterface):
    def get_present_crates(self)->list[Crate]:
        has_open_order = (
            select(Order.id)
            .where(
                or_(and_(Order.crate_id == Crate.id,
                         or_(Order.return_date == None,
                             Order.return_date >= datetime.combine(self.assign_date,time.min) + timedelta(hours=8))
                         ),
                    and_(Order.assigned_crate_id == Crate.id,
                         Order.delivery_date == self.assign_date))
            )
            .where(Order.deleted == False)
            .correlate(Crate)
            .exists()
        )
        return cast(list[Crate],
             self.session.exec(
                 select(Crate)
                 .where(~has_open_order)
                 .order_by(desc(Crate.last_seen))
             ).all()
             )
    def assign(self):
        for index, order in enumerate(self.orders):
            order.assigned_crate_id = None
            self.session.add(order)
            self.session.commit()
            self.session.refresh(self.orders[index])
        if len(self.orders) == 0:
            return
        if len(self.get_present_crates())< len(self.orders):
            raise Exception("Not enough crates")
        #search perfect_crates
        for order in self.orders:
            present_crates = self.get_present_crates()
            for crate in present_crates:
                crate_last_order = self.session.exec(
                    select(Order)
                    .where(Order.crate_id == crate.id)
                    .order_by(desc(Order.delivery_date))
                ).first()
                if crate_last_order.customer_id == order.customer_id:
                    order.assigned_crate_id = crate.id
                    break
            self.session.add(order)
            self.session.commit()

        for order in self.orders:
           if order.assigned_crate_id is None:
               order.assigned_crate_id = self.get_present_crates()[0].id
               self.session.add(order)
               self.session.commit()



        self.orders = cast(list[Order],
                           self.session.exec(select(Order).where(Order.delivery_date == self.assign_date)).all())
