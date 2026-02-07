from fastapi import APIRouter, Header, HTTPException, Depends
from .customer import  router as customers_router
from .invoice import router as invoices_router
from  .export import router as export_router

from ...shared.auth import authorize
from app.shared.dependencies import  CurrentUserDep


def auth(user:CurrentUserDep):
    return authorize(["admin"],user)
router = APIRouter(

    dependencies=[Depends(auth)]
)
router.include_router(customers_router, prefix="/customer")
router.include_router(  invoices_router,prefix="/invoice")
router.include_router(export_router, prefix="/export")

