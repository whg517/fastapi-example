from datetime import datetime
from typing import TypeVar

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import declarative_base, declared_attr, relationship


class CustomsBase:
    """
    自定义初始化规则
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id = Column(Integer, primary_key=True)


BaseModel = declarative_base(cls=CustomsBase)


class City(BaseModel):
    """City model"""
    name = Column(String(255))


class User(BaseModel):
    """User model"""
    name = Column(String(255))
    age = Column(Integer)

    city_id = Column(Integer, ForeignKey('city.id', ondelete='CASCADE'), nullable=True)
