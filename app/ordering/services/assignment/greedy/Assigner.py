
from sqlmodel import select, exists, func, desc
from sqlalchemy.orm import aliased

from app.accounting.models import Customer
from app.ordering.models import Order, Crate
from app.ordering.services.assignment.interface import AssignmentServiceInterface


class GreedyAssigner(AssignmentServiceInterface):
    def assign(self):
        crate_alias = aliased(Crate)
        present_statement =select(crate_alias).where(~Crate.orders.any(Order.return_date == None))

        for current_order in self.orders:
            newest_order_sub = (
                select(Order.id)
                .where(Order.crate_id == crate_alias.id)
                .where(Order.customer_id == current_order.customer_id)
                .order_by(desc(Order.delivery_date))
                .limit(1)
                .scalar_subquery()
                .correlate(crate_alias)
            )
            perfect_crate = self.session.exec(present_statement.where(Order.id == newest_order_sub)).first()
            if perfect_crate:
                current_order.crate = perfect_crate
                self.session.add(current_order)
            else:
                crate = self.session.exec(present_statement.order_by(desc(Crate.last_seen))).first()
                current_order.crate = crate
                self.session.add(current_order)
        self.session.refresh(self.orders)









