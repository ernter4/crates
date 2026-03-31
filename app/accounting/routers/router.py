from fastapi import APIRouter, Depends

from .customer import router as customer_router
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
router.include_router(  customer_router,prefix="/customer")
router.include_router(  invoices_router,prefix="/invoice")
router.include_router(export_router, prefix="/export")

