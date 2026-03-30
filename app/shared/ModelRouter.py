from typing import Generic, TypeVar, Type, Any, get_args
from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import SQLModel

from .ModelService import ModelService
from .dependencies import SessionDep, CurrentUserDep

TService = TypeVar("TService", bound=ModelService)
TCreate = TypeVar("TCreate")
TUpdate = TypeVar("TUpdate")
TOut = TypeVar("TOut")



class BaseRouter(Generic[TService, TCreate, TUpdate, TOut]):
    def __init__(self, service_class: Type[TService],ressource_name: str=""):
        self.resource_name = ressource_name
        self.service_class = service_class
        self.router = APIRouter()
        self._register_routes()


    def _register_routes(self):
        self.router.add_api_route(
            path="/"
            , endpoint=self.create
            , methods=["POST"]
            ,response_model=TOut
            , operation_id=self.resource_name.lower() + "_create"
        )
        self.router.add_api_route(
            path="/"
            , endpoint=self.update
            , methods=["PUT"]
            , response_model=TOut
            , operation_id=self.resource_name.lower() + "_put"
        )
        self.router.add_api_route(
            path="/{item_id}",
            endpoint=self.get,
            methods=["GET"],
             response_model = TOut,
            operation_id=self.resource_name.lower() + "_get_by_id")
        self.router.add_api_route(
            path= "/",
            endpoint=self.get_filtered,
            methods=["GET"],
            operation_id=self.resource_name.lower() + ""

        )

    def create(self, data: TCreate, session: SessionDep,current_user: CurrentUserDep):
        return self.service_class(session,current_user).create(data)

    def get(self, item_id: int, session: SessionDep,current_user: CurrentUserDep) -> TOut:
        return self.service_class(session,current_user).get(item_id)

    def update(self, data: TUpdate, session: SessionDep,current_user: CurrentUserDep ):
        try:
            return self.service_class(session).update(data, current_user)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))
    def get_filtered(self,*args, **kwargs):
        raise NotImplementedError
