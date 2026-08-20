from typing import cast

from sqlmodel import Session, select, desc

from datetime import date

from app.accounting.models import Customer, CustomerWithID, BaseCustomer
from app.ordering.models import Order, Assignment, Crate


class AssignmentServiceInterface:
    def __init__(self, session: Session, assign_date: date):
        self.session = session
        self.assign_date = assign_date
        self.orders: list[Order] = list(self.session.exec((select(Order)
                                                           .join(Crate, Crate.id == Order.assigned_crate_id,
                                                                 isouter=True)
                                                           .where(Order.delivery_date == self.assign_date)
                                                           .where(Order.crate_id == None)
                                                           .where(Order.deleted == False)
                                                           .order_by(desc(Crate.last_seen))
                                                           )
                                                          ).all())

    def assign(self):
        raise NotImplementedError

    def get_Assignment(self) -> list[Assignment]:
        assignments: list[Assignment] = []
        for current_order in self.orders:
            assignment = Assignment(order=current_order, card_swap=False, card_turn=False)
            last_order = self.session.exec(
                select(Order).where(Order.crate_id == current_order.assigned_crate_id).where(Order.deleted==False).order_by(
                    desc(Order.delivery_date))).first()
            if last_order.customer_id == current_order.customer_id:
                assignment.card_swap = False
            else:
                assignment.card_swap = True
            if last_order.menu_id == current_order.menu_id:
                assignment.card_turn = False
            else:
                assignment.card_turn = True
            assignments.append(assignment)
        return assignments

    def get_new_customer_cards(self) -> list[CustomerWithID]:
        customers: list[CustomerWithID] = []
        for assignment in self.get_Assignment():
            if assignment.card_swap:
                customers.append(self.session.get(Customer, assignment.order.customer_id))

        return customers
