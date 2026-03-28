from sqlmodel import Session, select, desc

from app.ordering.models import Order, AssignmentChanges
from datetime import date

class AssignmentServiceInterface:
    def __init__(self,session:Session,assign_date:date):
        self.session= session
        self.assign_date= assign_date
        self.orders: list[Order] = []
    def assign(self):
        raise NotImplementedError
    def get_changes(self):
        changes:list[AssignmentChanges] = []
        for current_order in self.orders:
            last_order = self.session.exec(select(Order).where(Order.crate== current_order.crate).where(Order.delivery_date< current_order.delivery_date).order_by(desc(Order.delivery_date))).first()
            if last_order is  None or  last_order.customer != current_order.customer:
                assignment_change = AssignmentChanges(order=current_order,old_customer=last_order.customer)
                changes.append(assignment_change)
        return changes
