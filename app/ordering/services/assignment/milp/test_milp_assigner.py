from datetime import date, datetime, timedelta

import pytest
from dotenv import load_dotenv
from sqlmodel import Session

load_dotenv()

from app.accounting.models import Customer
from app.ordering.models import Crate, Order
from app.ordering.services.assignment.milp.Assigner import MilpAssigner
from app.shared.database import engine

ASSIGN_DATE = date(2026, 7, 1)


def test_milp_assigner():
    """Nutzt die reguläre (in app.shared.database konfigurierte) Datenbank.

    Die Testdaten laufen in einer Transaktion, die am Ende immer zurückgerollt
    wird - die echte Datenbank bleibt dadurch unverändert.
    """
    with Session(engine) as session:
        assigner = MilpAssigner(session, ASSIGN_DATE)
        assigner.assign()


