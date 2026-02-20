from fastapi import APIRouter, Depends

from app.shared.auth import authorize
from app.shared.dependencies import CurrentUserDep
from .inventory import  router as inventory_router

def auth(user:CurrentUserDep):
    return authorize(["admin"],user)
router = APIRouter(
    dependencies=[Depends(auth)]
)
router.include_router(inventory_router,prefix="/inventory")
