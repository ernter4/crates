
from sqlmodel import select, exists, func, desc
from sqlalchemy.orm import aliased

from app.accounting.models import Customer
from app.ordering.models import Order, Crate
from app.ordering.services.assignment.interface import AssignmentServiceInterface


class GreedyAssigner(AssignmentServiceInterface):
    def assign(self):
        self.orders  = list(self.session.exec(select (Order).where(Order.delivery_date == self.assign_date)).all())
        crate_alias = aliased(Crate)
        present_statement =select(crate_alias).where(~Crate.orders.any(Order.return_date == None))

        for current_order in self.orders:
            newest_order= select(Order).where(Order.crate == crate_alias).where(Order.customer == current_order.customer).subquery()
            perfect_crate = self.session.exec(present_statement.where(Order == newest_order)).first()
            if perfect_crate:
                current_order.crate = perfect_crate
                self.session.add(current_order)
            else:
                crate = self.session.exec(present_statement.order_by(desc(Crate.last_seen))).first()
                current_order.crate = crate
                self.session.add(current_order)
        self.session.refresh(self.orders)









