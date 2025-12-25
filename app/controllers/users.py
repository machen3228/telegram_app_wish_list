from litestar import Controller, delete, get, post
from litestar.dto import DataclassDTO

from core.db import get_session
from domain.users import User
from dto.users import UserCreateDTO
from services.users import UserService


class UserController(Controller):
    path = '/users'

    @post()
    async def add(self, data: UserCreateDTO) -> dict[str, int]:
        async with get_session() as session:
            service = UserService(session)
            tg_id = await service.add(**data.__dict__)
            return {'tg_id': tg_id}

    @get('/{tg_id:int}', return_dto=DataclassDTO[User])
    async def get(self, tg_id: int) -> User:
        async with get_session() as session:
            service = UserService(session)
            return await service.get(tg_id)

    @post('/{friend_id:int}')
    async def add_friend(self, friend_id: int) -> None:
        pass

    @delete('/{friend_id:int}')
    async def delete_friend(self, friend_id: int) -> None:
        pass
