from fastapi import APIRouter, Depends

from app.shared.auth import authorize
from app.shared.dependencies import CurrentUserDep
from .inventory import  router as inventory_router
from .crate import router as crate_router
from.order import router as order_router
from .assigner import  router as assigner_router
def auth(user:CurrentUserDep):
    return authorize(["admin"],user)
router = APIRouter(
    dependencies=[Depends(auth)]
)
router.include_router(inventory_router,prefix="/inventory")
router.include_router(crate_router,prefix="/crate")

router.include_router(order_router,prefix="/order")
router.include_router(assigner_router,prefix="/assigner")