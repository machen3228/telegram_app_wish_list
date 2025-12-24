from litestar import Controller, delete, get, patch, post

from core.db import get_session
from schemas.users import UserCreateDTO
from services.users import UserService


class UserController(Controller):
    path = '/users'

    @post()
    async def create_user(self, data: UserCreateDTO) -> dict[str, str]:
        async with get_session() as session:
            service = UserService(session)
            await service.create_user(**data.model_dump())
            return {'hello': 'world'}

    @get('/{user_id:int}')
    async def get_user(self, user_id: int) -> None:
        pass

    @patch('/{user_id:int}')
    async def partial_update_user(self, user_id: int) -> None:
        pass

    @delete('/{user_id:int}')
    async def delete_user(self, user_id: int) -> None:
        pass

    @post('/{friend_id:int}')
    async def add_friend(self, friend_id: int) -> None:
        pass

    @delete('/{friend_id:int}')
    async def delete_friend(self, friend_id: int) -> None:
        pass
