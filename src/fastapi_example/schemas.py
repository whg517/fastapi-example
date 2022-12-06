from pydantic import BaseModel


class UserCreate(BaseModel):
    city: str
    name: str
    age: int


class User(BaseModel):
    name: str
    age: int
    city_id: int

    class Config:
        orm_mode = True
