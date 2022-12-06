import logging

from fastapi import APIRouter, FastAPI

from fastapi_example.schemas import UserCreate
from fastapi_example.services import UserService


def init_router(app: FastAPI):
    router_v1 = APIRouter(
    )

    router_v1.include_router(user_router, prefix='/user')
    app.include_router(router_v1, prefix='/v1')


user_router = APIRouter()

logger = logging.getLogger(__name__)


def common_parameters(foo: str):
    return {'foo': foo}


@user_router.get('/')
async def user_get(
):

    return await UserService().get_all()


@user_router.post('/')
async def user_create(obj_in: UserCreate):

    obj = await UserService().create(obj_in)
    return obj
