"""
base repository
"""
import dataclasses
import logging

from sqlalchemy import delete, func
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi_example.models import City, User
from fastapi_sqlalcmemy.extension import db

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class BaseRepository:
    """
    仓储对象基类
    """

    _session: AsyncSession | None = dataclasses.field(init=False, default=None)

    @property
    def model(self):
        """
        对象模型
        :return:
        """
        raise NotImplementedError()

    @property
    def session(self) -> AsyncSession:
        if not self._session:
            self._session = db.session
        logger.info(f'session in repo, session id: {id(self._session)}')
        return self._session

    async def get_all(self):
        """
        get all
        :return:
        """
        result: Result = await self.session.execute(select(self.model))
        return result.scalars().all()

    async def get(
            self,
            /,
            **kwargs,
    ):
        """
        条件查找
        :param kwargs:
        :return:
        """

        and_condition = [getattr(self.model, k) == v for k, v in kwargs.items()]
        stmt = select(self.model).filter(*and_condition)
        result = await self.session.scalars(stmt)
        return result.all()

    async def get_one_or_none(self, /, **kwargs):
        """
        通过条件获取一个对象，如果没有则返回 None
        :param kwargs:
        :return:
        """
        and_condition = [getattr(self.model, k) == v for k, v in kwargs.items()]
        stmt = select(self.model).filter(*and_condition)
        result = await self.session.scalars(stmt)
        return result.one_or_none()

    async def get_or_create(self, /, params: dict = None, **kwargs):
        """
        根据 kwargs 参数查询对象，如果对象不存在，使用 params 参数更新 kwargs 后创建对象并返回。
        通过 kwargs 参数查询的结果必须只有一个对象。
        :param params:
        :param kwargs:
        :return:
        """
        obj = await self.get_one_or_none(**kwargs)
        logger.debug('get object %s', obj)
        if not obj:
            # 用 params 更新参数，然后创建对象
            kwargs.update(params or {})
            obj = await self.create(**kwargs)

        logger.debug('get or create object %s', obj)
        return obj

    async def get_by_id(self, pk: int):
        """
        通过 id 查找对象
        :param pk:
        :return:
        """
        result = await self.session.get(self.model, pk)
        if result:
            return result

    async def create(self, /, **kwargs):
        """
        创建对象
        :param kwargs:
        :return:
        """
        obj = self.model(**kwargs)
        logger.info(f'repo create session: {id(self.session)}')
        self.session.add(obj)
        await self.session.flush()
        # await self.session.commit()
        return obj

    async def update(self, pk: int, **kwargs):
        """
        更新对象
        :param pk:
        :param kwargs:
        :return:
        """
        obj = await self.get_by_id(pk)
        for k, v in kwargs.items():
            setattr(obj, k, v)
        await self.session.flush()
        return obj

    async def delete(self, pk: int) -> None:
        """
        删除对象
        :param pk:
        :return:
        """
        stmt = delete(self.model).where(self.model.id == pk)
        await self.session.execute(stmt)

    async def count(
            self,
            **kwargs
    ) -> int:
        """
        获取总和
        :return:
        """
        and_condition = [getattr(self.model, k) == v for k, v in kwargs.items()]
        stmt = select(func.count()).filter(*and_condition).select_from(self.model)
        total = await self.session.scalar(stmt)
        return total


class CityRepository(BaseRepository):
    @property
    def model(self):
        """
        对象模型
        :return:
        """
        return City


class UserRepository(BaseRepository):

    @property
    def model(self):
        return User
