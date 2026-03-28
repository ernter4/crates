from pydantic.v1 import BaseModel
from sqlmodel import SQLModel, select
from sqlmodel import Select
from app.shared.models import ModelWithId


class ModelService:
    def __init__(self):
        self.create_model:SQLModel
        self.update_model:SQLModel = SQLModel
        self.base_model:SQLModel = SQLModel
    @staticmethod
    def update(self,element:ModelWithId):
        model = session select(BaseModel).where (self.base_model.id == element.id).first()


