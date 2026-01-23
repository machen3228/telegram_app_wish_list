from litestar import Controller, Request, delete, get, post
from litestar.dto import DataclassDTO

from core.db import get_session
from core.security import verify_telegram_auth
from domain.users import User
from services.users import UserService


class UserController(Controller):
    path = '/users'
    tags = ('Users',)

    @post('/auth', return_dto=DataclassDTO[User], status_code=201)
    async def telegram_login(self, request: Request) -> User:
        data = await request.json()
        verified_data = verify_telegram_auth(data)

        tg_id = verified_data['id']
        username = verified_data['username']
        first_name = verified_data['first_name']
        last_name = verified_data['last_name']

        async with get_session() as session:
            service = UserService(session)
            try:
                user = await service.get(tg_id)
            except KeyError:
                user = await service.add(
                    tg_id=tg_id,
                    tg_username=username,
                    first_name=first_name,
                    last_name=last_name,
                    birthday=None,
                )
        return user

    @get('/{tg_id:int}', return_dto=DataclassDTO[User], summary='Get user')
    async def get(self, tg_id: int) -> User:
        async with get_session() as session:
            service = UserService(session)
            return await service.get(tg_id)

    @post('/{tg_id:int}/{friend_id:int}', status_code=201, summary='Add new friend')
    async def add_friend(self, tg_id: int, friend_id: int) -> dict[str, str]:
        async with get_session() as session:
            service = UserService(session)
            await service.add_friend(tg_id, friend_id)
            return {'message': 'Friend was added'}

    @delete('/{tg_id:int}/{friend_id:int}', status_code=204, summary='Delete friend')
    async def delete_friend(self, tg_id: int, friend_id: int) -> None:
        async with get_session() as session:
            service = UserService(session)
            await service.delete_friend(tg_id, friend_id)
