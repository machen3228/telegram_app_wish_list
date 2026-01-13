from litestar import Controller, delete, get, post
from litestar.dto import DataclassDTO

from core.db import get_session
from domain.users import User
from dto.users import UserCreateDTO
from services.users import UserService


class UserController(Controller):
    path = '/users'

    @post(status_code=201)
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

    @post('/{tg_id:int}/{friend_id:int}', status_code=201)
    async def add_friend(self, tg_id: int, friend_id: int) -> dict[str, str]:
        async with get_session() as session:
            service = UserService(session)
            await service.add_friend(tg_id, friend_id)
            return {'message': 'Friend was added'}

    @delete('/{tg_id:int}/{friend_id:int}', status_code=204)
    async def delete_friend(self, tg_id: int, friend_id: int) -> None:
        async with get_session() as session:
            service = UserService(session)
            await service.delete_friend(tg_id, friend_id)
