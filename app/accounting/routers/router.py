from fastapi import APIRouter, Depends

from .customer import router as customer_router


from ..services.models.customerService import CustomerService

from ...shared.auth import authorize
from app.shared.dependencies import  CurrentUserDep


def auth(user:CurrentUserDep):
    return authorize(["admin"],user)
router = APIRouter(
    dependencies=[Depends(auth)]
)
router.include_router(  customer_router,prefix="/customer")


