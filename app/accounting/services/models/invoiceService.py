from sqlmodel import Session

from app.accounting.models import Invoice, InvoiceWithID
from app.shared.ModelService import ModelService


class InvoiceService(ModelService[Invoice,Invoice,InvoiceWithID,InvoiceWithID]):
    def __init__(self, session: Session):
        super().__init__(session, Invoice,InvoiceWithID)

    def create