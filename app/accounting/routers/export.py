from fastapi import APIRouter
from ..dependencies import ExportServiceDep
from ..models import CreateAccountingExport
router = APIRouter()

@router.post("/")
def create_export(new_export: CreateAccountingExport, export_service: ExportServiceDep):
    return export_service.create_export(new_export)
