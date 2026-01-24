from typing import Annotated

from fastapi import Depends

from .services.export_service import ExportService
from ..shared.dependencies import SessionDep


def get_export_service(session :SessionDep) -> ExportService:
    return ExportService(session)
ExportServiceDep = Annotated[ExportService, Depends(get_export_service)]