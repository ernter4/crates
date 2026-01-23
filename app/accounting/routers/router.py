from fastapi import APIRouter
from .customer import  router as customers_router
from .invoice import router as invoices_router

router = APIRouter()
router.include_router(customers_router, prefix="/customers")
router.include_router(  invoices_router,prefix="/invoices")
