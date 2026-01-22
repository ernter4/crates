from fastapi import APIRouter
from .customers import  router as customers_router
from .invoices import router as invoices_router

router = APIRouter()
router.include_router(customers_router, prefix="/customers")
router.include_router(  invoices_router,prefix="/invoices")
