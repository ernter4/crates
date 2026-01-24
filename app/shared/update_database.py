import logging

from fastapi import HTTPException
from sqlmodel import SQLModel

from sqlmodel import Session
logger = logging.getLogger(__name__)

def update_database(model_instance:SQLModel, session: Session):
    try:
        session.add(model_instance)
        session.commit()
        session.refresh(model_instance)
    except Exception as e:
        session.rollback()
        logger.error(f"Error in database :{e}")
        raise HTTPException(status_code=400, detail=f"Database operation failed for { model_instance.__class__.__name__}")
    return model_instance

def delete_from_database(model_instance:SQLModel, session: Session):
    try:
        session.delete(model_instance)
        session.commit()
        return {"detail" : f"{ model_instance.__class__.__name__} with id {model_instance.id} deleted successfully"}
    except Exception as e:
        session.rollback()
        logger.error(f"Error in database : {e}")
        raise HTTPException(status_code=400, detail=f"Database delete operation failed for { model_instance.__class__.__name__}")