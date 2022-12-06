"""Test config"""
import asyncio
import logging

import pytest
from click.testing import CliRunner
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from fastapi_example.config import settings
from fastapi_example.models import City, BaseModel
from fastapi_sqlalcmemy.extension import db

logger = logging.getLogger(__name__)


@pytest.fixture(autouse=True)
def migrate():
    """migrate fixture"""

    async def setup():
        """setup"""
        _engine: AsyncEngine = create_async_engine(
            settings.DATABASE,
            future=True,
        )
        async with _engine.begin() as conn:
            await conn.run_sync(BaseModel.metadata.drop_all)
            await conn.run_sync(BaseModel.metadata.create_all)
        await _engine.dispose()

    asyncio.run(setup())
    yield


@pytest.fixture()
def clicker():
    """clicker fixture"""
    yield CliRunner()


@pytest.fixture(autouse=True)
def db_init():
    db.init_db(settings.DATABASE)


@pytest.fixture()
def session_ctx():
    token = db.set_session_ctx()
    yield
    db.reset_session_ctx(token)


@pytest.fixture()
async def session(session_ctx):
    """"""
    async with db.session.begin():
        yield db.session


@pytest.fixture()
async def init_city():
    async with db():
        objs = [
            City(name='sh'),
            City(name='bj')
        ]
        db.session.add_all(objs)
        db.session.commit()
