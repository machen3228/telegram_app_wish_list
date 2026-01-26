import json

from litestar import Controller, delete, get, post
from litestar.di import Provide
from litestar.dto import DataclassDTO
from litestar.exceptions import HTTPException

from core.auth import validate_telegram_init_data
from core.config import settings
from core.db import get_session
from core.dependencies import get_current_user_id
from domain.users import Gift, User
from dto.users import TelegramAuthDTO
from services.gifts import GiftService
from services.users import UserService


class UserController(Controller):
    path = '/users'
    tags = ('Users',)

    @post('/auth/telegram', summary='Telegram Mini App auth')
    async def telegram_login(self, data: TelegramAuthDTO) -> User:
        if not data.init_data:
            raise HTTPException(status_code=401, detail='Missing init_data')
        try:
            validated_data = validate_telegram_init_data(data.init_data, settings.bot.token.get_secret_value())
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

    @get(
        '/me',
        return_dto=DataclassDTO[User],
        summary='Get current user',
        dependencies={'current_user_id': Provide(get_current_user_id)},
    )
    async def get_me(self, current_user_id: int) -> User:
        async with get_session() as session:
            service = UserService(session)
            return await service.get(current_user_id)

    @post(
        '/me/friends/{friend_id:int}',
        status_code=201,
        summary='Add new friend',
        dependencies={'current_user_id': Provide(get_current_user_id)},
    )
    async def add_friend(self, current_user_id: int, friend_id: int) -> dict[str, str]:
        async with get_session() as session:
            service = UserService(session)
            await service.add_friend(current_user_id, friend_id)
            return {'message': 'Friend was added'}

    @delete(
        '/me/friends/{friend_id:int}',
        status_code=204,
        summary='Delete friend',
        dependencies={'current_user_id': Provide(get_current_user_id)},
    )
    async def delete_friend(self, current_user_id: int, friend_id: int) -> None:
        async with get_session() as session:
            service = UserService(session)
            await service.delete_friend(current_user_id, friend_id)

    @get(
        '/me/friends',
        summary='Get my friends with details',
        dependencies={'current_user_id': Provide(get_current_user_id)},
    )
    async def get_my_friends(self, current_user_id: int) -> list[User]:
        async with get_session() as session:
            service = UserService(session)
            return await service.get_friends(current_user_id)

    @get('/{tg_id:int}', return_dto=DataclassDTO[User], summary='Get user')
    async def get_user(self, tg_id: int) -> User:
        async with get_session() as session:
            service = UserService(session)
            return await service.get(tg_id)

    @get('/{tg_id:int}/gifts', summary='Get user wishlist')
    async def get_user_gifts(self, tg_id: int) -> list[Gift]:
        async with get_session() as session:
            service = GiftService(session)
            return await service.get_gifts_by_user_id(tg_id)
