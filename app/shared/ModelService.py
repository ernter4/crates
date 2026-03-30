from typing import Generic, TypeVar, Type, Optional

from sqlmodel.sql.expression import SelectOfScalar
from sqlmodel import SQLModel, Session, select

from app.shared.models import ModelWithId, User

TDatabase = TypeVar("TDatabase", bound=ModelWithId)
TCreate = TypeVar("TCreate", bound=SQLModel)
TUpdate = TypeVar("TUpdate", bound=ModelWithId)
Tout = TypeVar("Tout", bound=ModelWithId)
TFilter = TypeVar("TFilter",bound=SQLModel)

class ModelService(Generic[TDatabase, TCreate, TUpdate, Tout]):
    def __init__(self, session: Session,model_class: Type[TDatabase], out_class: Type[Tout],current_user:User = None):
        self.session = session
        self.current_user: Optional[User] = current_user
        self.model_class = model_class
        self.out_class = out_class


    def create(self, data: TCreate) -> Tout:
        # Erstellt DB-Objekt aus Create-Daten
        db_obj = self.model_class.model_validate(data)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        # Validiert das Ergebnis gegen das Output-Model (TOUT)
        return self.out_class.model_validate(db_obj)
    def get(self,item_id:int) -> Tout:
        return self.session.get(self.model_class,item_id)

    def update(self, data: TUpdate) -> Tout:
        # ID direkt aus dem übergebenen Objekt ziehen
        obj_id: int = data.id

        db_obj = self.session.get(self.model_class, obj_id)
        if not db_obj:
            raise ValueError(f"Eintrag mit ID {obj_id} nicht gefunden.")

        # Update nur mit den Feldern, die im Objekt gesetzt wurden
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)

        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return self.out_class.model_validate(db_obj)
    def get_filtered(self, filter: TFilter) -> list[Tout]:
        filter_statement = select(self.model_class)
        for key, value in filter.model_dump(exclude_none=True).items():
            if key.endswith("_exists"):
                filter_statement = filter_statement.where(getattr(self.model_class, key[:-7]) is not None)
            else:
                filter_statement = filter_statement.where(getattr(self.model_class, key) == value)

        results = self.session.exec(filter_statement).all()
        return [self.out_class.model_validate(row) for row in results]

