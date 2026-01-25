import json

from litestar import Controller, delete, get, post
from litestar.dto import DataclassDTO
from litestar.exceptions import HTTPException

from core.auth import validate_telegram_init_data
from core.db import get_session
from domain.users import User
from dto.users import TelegramAuthDTO
from services.users import UserService


class UserController(Controller):
    path = '/users'
    tags = ('Users',)

    @post('/auth/telegram', summary='Telegram Mini App auth')
    async def telegram_login(self, data: TelegramAuthDTO) -> User:
        if not data.init_data:
            raise HTTPException(status_code=401, detail='Missing init_data')
        try:
            validated_data = validate_telegram_init_data(data.init_data)
        except ValueError as e:
            raise HTTPException(status_code=401, detail=f'Invalid init_data: {e!s}') from None
        user_json = validated_data.get('user')
        if not user_json:
            raise HTTPException(status_code=401, detail='User data not found in init_data')
        user_data = json.loads(user_json)
        async with get_session() as session:
            service = UserService(session)
            try:
                user = await service.get(user_data['id'])
            except HTTPException:
                user = await service.add(
                    tg_id=user_data['id'],
                    tg_username=user_data.get('username', ''),
                    first_name=user_data.get('first_name', ''),
                    last_name=user_data.get('last_name', ''),
                    avatar_url=user_data.get('photo_url', ''),
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
