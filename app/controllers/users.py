from litestar import Controller, delete, get, post
from litestar.di import Provide
from litestar.dto import DataclassDTO

from core.db import get_session
from core.dependencies import get_current_user_id
from domain.gifts import Gift
from domain.users import User
from dto.users import FriendRequestDTO, TelegramAuthDTO
from services.gifts import GiftService
from services.users import UserService


class UserController(Controller):
    path = '/users'
    tags = ('Users',)

    @post('/auth/telegram', summary='Telegram Mini App auth')
    async def telegram_login(self, data: TelegramAuthDTO) -> User:
        async with get_session() as session:
            service = UserService(session)
            return await service.telegram_login(data)

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

    @get('/{tg_id:int}', return_dto=DataclassDTO[User], summary='Get user')
    async def get_user(self, tg_id: int) -> User:
        async with get_session() as session:
            service = UserService(session)
            return await service.get(tg_id)

    @get(
        '/{tg_id:int}/gifts',
        summary='Get user wishlist',
        dependencies={'current_user_id': Provide(get_current_user_id)},
    )
    async def get_user_gifts(self, tg_id: int, current_user_id: int) -> list[Gift]:
        async with get_session() as session:
            service = GiftService(session)
            return await service.get_gifts_by_user_id(tg_id, current_user_id)

    @post(
        '/me/friends/{receiver_id:int}/request',
        status_code=201,
        summary='Send friend request',
        dependencies={'current_user_id': Provide(get_current_user_id)},
    )
    async def send_friend_request(self, current_user_id: int, receiver_id: int) -> dict[str, str]:
        async with get_session() as session:
            service = UserService(session)
            await service.send_friend_request(current_user_id, receiver_id)
            return {'message': 'Friend request sent'}

    @get(
        '/me/friend-requests',
        status_code=200,
        summary='Get pending friend requests',
        dependencies={'current_user_id': Provide(get_current_user_id)},
    )
    async def get_friend_requests(self, current_user_id: int) -> list[FriendRequestDTO]:
        async with get_session() as session:
            service = UserService(session)
            return await service.get_pending_requests(current_user_id)

    @post(
        '/me/friends/{sender_id:int}/accept',
        status_code=200,
        summary='Accept friend request',
        dependencies={'current_user_id': Provide(get_current_user_id)},
    )
    async def accept_friend_request(self, current_user_id: int, sender_id: int) -> dict[str, str]:
        async with get_session() as session:
            service = UserService(session)
            await service.accept_friend_request(current_user_id, sender_id)
            return {'message': 'Friend request accepted'}

    @post(
        '/me/friends/{sender_id:int}/reject',
        status_code=200,
        summary='Reject friend request',
        dependencies={'current_user_id': Provide(get_current_user_id)},
    )
    async def reject_friend_request(self, current_user_id: int, sender_id: int) -> dict[str, str]:
        async with get_session() as session:
            service = UserService(session)
            await service.reject_friend_request(current_user_id, sender_id)
            return {'message': 'Friend request rejected'}

    @delete(
        '/me/friends/{friend_id:int}/delete',
        status_code=204,
        summary='Delete friend (mutual)',
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
