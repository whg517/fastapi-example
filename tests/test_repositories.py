import asyncio
import logging

import pytest
from sqlalchemy import func, select

from fastapi_example.models import City
from fastapi_example.repositories import CityRepository
from fastapi_sqlalcmemy.extension import db

logger = logging.getLogger(__name__)


@pytest.fixture()
async def repo():
    yield CityRepository()


async def test_create(
        init_city,
        repo,
        session
):
    """"""
    await repo.create(
        name='xxx'
    )
    # session = session
    session = db.session
    logger.info(f'test create session: {id(session)}')
    count = await session.scalar(select(func.count()).select_from(City))
    assert count == 3
    # count = await repo.count()
    # assert count == 3

#
# async def test_delete(repo, session):
#     """"""
#     await repo.delete(2)
