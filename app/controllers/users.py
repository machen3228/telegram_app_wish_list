from litestar import Controller
from litestar import delete
from litestar import get
from litestar import patch
from litestar import post
from litestar.di import Provide
from litestar.dto import DataclassDTO

from core.security import TelegramInitData
from core.security import TokenOut
from dependencies import provide_access_jwt_auth
from dependencies import provide_telegram_init_data
from dependencies import provide_user_service
from domain import User
from dto.users import FriendRequestDTO
from services import UserService


class UserController(Controller):
    path = '/users'
    tags = ('Users',)
    dependencies = {'service': Provide(provide_user_service, sync_to_thread=False)}

    @post(
        '/auth',
        summary='Telegram Mini App auth',
        dependencies={'init_data': Provide(provide_telegram_init_data, sync_to_thread=False)},
    )
    async def telegram_login(
        self,
        service: UserService,
        init_data: TelegramInitData,
    ) -> TokenOut:
        return await service.telegram_login(init_data)

    @get(
        '/me',
        return_dto=DataclassDTO[User],
        summary='Get current user',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def get_me(
        self,
        service: UserService,
        current_user_id: int,
    ) -> User:
        return await service.get(current_user_id)

    @get('/{tg_id:int}', return_dto=DataclassDTO[User], summary='Get user')
    async def get_user(
        self,
        service: UserService,
        tg_id: int,
    ) -> User:
        return await service.get(tg_id)

    @post(
        '/me/friends/{receiver_id:int}/request',
        status_code=201,
        summary='Send friend request',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def send_friend_request(
        self,
        service: UserService,
        current_user_id: int,
        receiver_id: int,
    ) -> dict[str, str]:
        await service.send_friend_request(current_user_id, receiver_id)
        return {'message': 'Friend request has been sent'}

    @get(
        '/me/friend-requests',
        status_code=200,
        summary='Get pending friend requests',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def get_friend_requests(
        self,
        service: UserService,
        current_user_id: int,
    ) -> list[FriendRequestDTO]:
        return await service.get_pending_requests(current_user_id)

    @patch(
        '/me/friends/{sender_id:int}/accept',
        summary='Accept friend request',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def accept_friend_request(
        self,
        service: UserService,
        current_user_id: int,
        sender_id: int,
    ) -> dict[str, str]:
        await service.accept_friend_request(current_user_id, sender_id)
        return {'message': 'Friend request accepted'}

    @patch(
        '/me/friends/{sender_id:int}/reject',
        summary='Reject friend request',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def reject_friend_request(
        self,
        service: UserService,
        current_user_id: int,
        sender_id: int,
    ) -> dict[str, str]:
        await service.reject_friend_request(current_user_id, sender_id)
        return {'message': 'Friend request rejected'}

    @delete(
        '/me/friends/{friend_id:int}/delete',
        status_code=204,
        summary='Delete friend (mutual)',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def delete_friend(
        self,
        service: UserService,
        current_user_id: int,
        friend_id: int,
    ) -> None:
        await service.delete_friend(current_user_id, friend_id)

    @get(
        '/me/friends',
        summary='Get my friends with details',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def get_my_friends(
        self,
        service: UserService,
        current_user_id: int,
    ) -> list[User]:
        return await service.get_friends(current_user_id)
