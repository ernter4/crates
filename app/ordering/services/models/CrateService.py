from sqlmodel import Session

from app.ordering.models import CrateWithID, Crate
from app.shared.ModelService import ModelService



class CrateService(ModelService[Crate,Crate,Crate,CrateWithID]):
    def __init__(self, session: Session):
        super().__init__(session, Crate,CrateWithID)