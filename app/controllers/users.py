from litestar import Controller, delete, get, post

from core.db import get_session
from schemas.users import UserCreateDTO, UserReadDTO
from services.users import UserService


class UserController(Controller):
    path = '/users'

    @post()
    async def add(self, data: UserCreateDTO) -> dict[str, int]:
        async with get_session() as session:
            service = UserService(session)
            tg_id = await service.add(**data.model_dump())
            return {'tg_id': tg_id}

    @get('/{tg_id:int}')
    async def get(self, tg_id: int) -> UserReadDTO:
        async with get_session() as session:
            service = UserService(session)
            result = await service.get(tg_id)
            return UserReadDTO.model_validate(result)

    @post('/{friend_id:int}')
    async def add_friend(self, friend_id: int) -> None:
        pass

    @delete('/{friend_id:int}')
    async def delete_friend(self, friend_id: int) -> None:
        pass
