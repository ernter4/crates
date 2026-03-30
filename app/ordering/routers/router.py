from fastapi import APIRouter, Depends

from app.shared.auth import authorize
from app.shared.dependencies import CurrentUserDep
from .inventory import  router as inventory_router
#from.order import router as order_router
from .assigner import  router as assigner_router
from .order import OrderRouter
from ..models import OrderCreate, OrderWithID
from ..services.models.CrateService import CrateService
from ..services.models.order import OrderService
from ...shared.ModelRouter import BaseRouter


def auth(user:CurrentUserDep):
    return authorize(["admin"],user)
router = APIRouter(
    dependencies=[Depends(auth)]
)
router.include_router(inventory_router,prefix="/inventory")

crate_router =OrderRouter(service_class=CrateService,ressource_name="crate").router
order_router =OrderRouter(service_class=OrderService,ressource_name="order").router



router.include_router(crate_router,prefix="/crate")

router.include_router(order_router,prefix="/order")


router.include_router(assigner_router,prefix="/assigner")