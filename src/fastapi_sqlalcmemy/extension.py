import asyncio
import contextlib
import contextvars
import dataclasses
import logging
from typing import cast, ClassVar

import sqlalchemy as sa
import sqlalchemy.ext
import sqlalchemy.orm
import sqlalchemy.ext.asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from fastapi_sqlalcmemy.exceptions import SQLAlchemyNotInitError

logger = logging.getLogger(__name__)


class SingleMeta(type):
    """
    单例元类
    """
    __instance = None

    def __call__(cls, *args, **kwargs):
        if not cls.__instance:
            instance = super().__call__(*args, **kwargs)
            cls.__instances = instance
        return cls.__instances


class SQLAlchemy(metaclass=SingleMeta):

    def __init__(self):
        self.__engine: sa.ext.asyncio.engine.AsyncEngine | None = None
        self.__session_maker: sa.orm.sessionmaker | None = None
        self.__session_ctx: contextvars.ContextVar[
            sa.ext.asyncio.session.AsyncSession | None
            ] = contextvars.ContextVar("session_ctx", default=None)

    def init_db(
            self,
            url: str,
            echo: bool = False
    ):
        """

        :param url:
        :param echo:
        :return:
        """
        self.__engine = create_async_engine(
            url,
            echo=echo,
            future=True,
        )
        self.__session_maker = sa.orm.sessionmaker(
            self.engine,
            class_=sa.ext.asyncio.session.AsyncSession,
            # expire_on_commit=False,  # 取消提交后过期操作，此现象会产生缓存，请注意清理。
        )

    @property
    def session_ctx(self):
        return self.__session_ctx

    @property
    def session_maker(self):
        if self.__session_maker:
            return self.__session_maker
        raise SQLAlchemyNotInitError

    @property
    def engine(self):
        if self.__engine:
            return self.__engine
        raise SQLAlchemyNotInitError

    @property
    def session(self) -> AsyncSession:
        assert self.session_maker
        _session = self.__session_ctx.get()
        if not _session:
            _session = self.session_maker()
            logger.warning(f'Can not found session in Session ContextVar, so create free session')
        logger.info(f'Got sa session: {id(_session)}')
        return _session

    def set_session_ctx(self):
        assert self.session_maker
        session = self.session_maker()
        session = cast(AsyncSession, session)
        logger.info(f'Init context session, session id: {id(session)}')
        session_ctx_token = self.session_ctx.set(session)
        logger.info(f'Set session {id(session)} to context var, context var token: {session_ctx_token}')
        return session_ctx_token

    def reset_session_ctx(self, token):
        self.session_ctx.reset(token)

    @contextlib.asynccontextmanager
    async def __call__(self, *args, **kwargs):
        token = self.set_session_ctx()
        session = self.__session_ctx.get()
        session_id = id(session)
        async with session.begin():
            yield session
        await session.close()
        self.reset_session_ctx(token)
        logger.debug(f'Reset context var token {token}, and session id: {id(session_id)}')


db = SQLAlchemy()


def session_ctx(func: callable):
    async def _wrap(*args, **kwargs):
        async with db():
            result = await func(*args, **kwargs)
            return result

    return _wrap
