from fastapi import APIRouter, Depends

from .customer import router as customer_router
from .invoice import router as invoices_router
from  .export import router as export_router
from .tax_rate import router as tax_rate_router
from .article import router as article_router
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
router.include_router(tax_rate_router, prefix="/tax_rate")
router.include_router(article_router, prefix="/article")

