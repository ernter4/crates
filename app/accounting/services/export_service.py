import locale
from datetime import datetime, date
from sqlmodel import Session, select
from sepaxml import SepaDD
from app.accounting.models import CreateAccountingExport, AccountingExport,SepaStatement
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database
from app.accounting.models import Invoice
from .sepa.config import config


class ExportService:
    def __init__(self,session: SessionDep):
        self.session:Session = session
    def create_export(self, new_export: CreateAccountingExport)-> AccountingExport:
        export = AccountingExport(**new_export.model_dump(),created_at = datetime.now())
        update_database(export,self.session)
        self.create_sepa_export(export.start_date,export.end_date,export.id)
        return export
    def create_sepa_export(self,start_date: date, end_date: date, export_id:int) :
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
        query = select(Invoice)
        query.where(Invoice.billing_date >= start_date)
        query.where(Invoice.billing_date <= end_date)
        invoices = self.session.exec(query).all()
        sepa = SepaDD(config, schema="pain.008.001.02", clean=True)
        for invoice in invoices:
            payment = {
                "name": f"{invoice.customer.first_name} {invoice.customer.last_name}",
                "IBAN": invoice.customer.iban,
                "BIC": invoice.customer.bic,
                "amount": invoice.amount*100,
                "type": "RCUR",
                "collection_date": datetime.date.today(),
                "mandate_id": invoice.customer.sepa_mandate_reference,
                "mandate_date": datetime.date.today(),
                "description": f"Essen ausser Haus im Monat {invoice.billing_date.strftime('%B %Y')} - Rechnung Nr. {invoice.invoice_number}"}
            sepa.add_payment(payment)
        sepa_db = SepaStatement(export_id = export_id, sepa_xml = sepa.export(validate=True))
        update_database(sepa_db,self.session)



