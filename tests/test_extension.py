import asyncio

from fastapi_sqlalcmemy.extension import SQLAlchemy, session_ctx, db


async def test_session():
    db.init_db('sqlite+aiosqlite:////memory')

    async def foo():
        return db.session

    @session_ctx
    async def bar():
        return db.session

    async with db() as session:
        res = await foo()
        assert id(res) == id(session)

        fut = asyncio.create_task(foo())
        res = await fut
        assert id(res) == id(session)


