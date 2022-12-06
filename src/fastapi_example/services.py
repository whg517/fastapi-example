from fastapi_example.repositories import UserRepository, CityRepository
from fastapi_example.schemas import UserCreate


class UserService:
    user_repo = UserRepository()
    city_repo = CityRepository()

    async def get_all(self):
        objs = await self.user_repo.get_all()
        return objs

    async def create(self, obj_in: UserCreate):
        """"""
        city_obj = await self.city_repo.get_or_create(
            params={'name': obj_in.city},
            name=obj_in.city
        )

        user_obj = await self.user_repo.create(
            name=obj_in.name,
            age=obj_in.age,
            city_id=city_obj.id
        )
        return user_obj
