from sqlmodel import Session

from app.accounting.models import InvoiceItem, InvoiceItemWithID
from app.shared.ModelService import ModelService


class InvoiceItemService(ModelService[InvoiceItem,InvoiceItem,InvoiceItemWithID,InvoiceItemWithID]):
    def __init__(self, session: Session):
        super().__init__(session, InvoiceItem,InvoiceItemWithID)