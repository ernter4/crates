from fastapi import APIRouter, Depends

from .customer import CustomerRouter
from .invoice import router as invoices_router
from  .export import router as export_router
from ..services.models.customerService import CustomerService

from ...shared.auth import authorize
from app.shared.dependencies import  CurrentUserDep


def auth(user:CurrentUserDep):
    return authorize(["admin"],user)
router = APIRouter(
    dependencies=[Depends(auth)]
)
router.include_router(CustomerRouter(service_class=CustomerService,ressource_name="customer").router, prefix="/customer")
router.include_router(  invoices_router,prefix="/invoice")
router.include_router(export_router, prefix="/export")

