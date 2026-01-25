import locale
from datetime import datetime, date
from sqlmodel import Session, select
from sepaxml import SepaDD
from app.accounting.models import CreateAccountingExport, AccountingExport
from app.shared.dependencies import SessionDep
from app.shared.update_database import update_database
from app.accounting.models import Invoice
from .sepa.config import config


class ExportService:
    def __init__(self,session: SessionDep):
        self.session:Session = session
    def create_export(self, new_export: CreateAccountingExport)-> AccountingExport:
        export = AccountingExport(**new_export.model_dump(),created_at = datetime.now())
        export =update_database(export,self.session)
        export =self.create_sepa_export(export)
        return update_database(export,self.session)

    def create_sepa_export(self,export : AccountingExport) -> AccountingExport:
        locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')
        query = select(Invoice)
        query.where(Invoice.billing_date >= export.start_date)
        query.where(Invoice.billing_date <= export.end_date)
        invoices = self.session.exec(query).all()
        sepa = SepaDD(config, schema="pain.008.001.02", clean=True)
        for invoice in invoices:
            payment = {
                "name": f"{invoice.customer.first_name} {invoice.customer.last_name}",
                "IBAN": invoice.customer.iban,
                "BIC": invoice.customer.bic,
                "amount": int(invoice.amount*100),
                "type": "RCUR",
                "collection_date": date.today(),
                "mandate_id": invoice.customer.sepa_mandate_reference,
                "mandate_date": date.today(),
                "description": f"Essen ausser Haus im Monat {invoice.billing_date.strftime('%B %Y')} - Rechnung Nr. {invoice.invoice_number}"}
            sepa.add_payment(payment)
        export.sepa_xml = sepa.export(validate=True)
        return export



