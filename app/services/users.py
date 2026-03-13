from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import BaseJWTAuth
from core.security import TelegramInitData
from core.security import TokenOut
from domain import User
from domain.users import FriendAction
from dto.users import FriendRequestDTO
from exceptions.database import NotFoundInDbError
from exceptions.http import BadRequestError
from repositories import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repository = UserRepository(session)

    async def telegram_login(self, init_data: TelegramInitData) -> TokenOut:
        tg_id = init_data['id']
        try:
            user = await self._repository.get(tg_id)
            fields_to_update = user.get_changed_fields(init_data)
            if fields_to_update:
                await self._repository.update(tg_id, **fields_to_update)
                logger.info('User profile updated: tg_id={}', tg_id)
        except NotFoundInDbError:
            logger.info('New user registration: tg_id={}', tg_id)
            await self.add(
                tg_id=tg_id,
                tg_username=init_data.get('username', ''),
                first_name=init_data.get('first_name', ''),
                last_name=init_data.get('last_name', ''),
                avatar_url=init_data.get('photo_url', ''),
            )
        except Exception as e:
            logger.error('Unexpected error during telegram login for tg_id={}: {}', tg_id, type(e).__name__)
            raise

        logger.success('User authenticated and logged in: tg_id={}', tg_id)
        return BaseJWTAuth.create_token(tg_id)

    async def add(
        self,
        tg_id: int,
        tg_username: str | None,
        first_name: str | None,
        last_name: str | None,
        avatar_url: str | None,
    ) -> User:
        user = User.create(
            tg_id=tg_id,
            tg_username=tg_username,
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
        )
        try:
            tg_id = await self._repository.add(user)
            logger.success('User created successfully: tg_id={}', tg_id)
            return await self._repository.get(tg_id)
        except Exception as e:
            logger.error('Failed to create user with tg_id={}: {}', tg_id, type(e).__name__)
            raise

    async def get(self, tg_id: int) -> User:
        try:
            result = await self._repository.get(tg_id)
            logger.success('User retrieved successfully: tg_id={}', tg_id)
        except Exception as e:
            logger.error('Failed to retrieve user with tg_id={}: {}', tg_id, type(e).__name__)
            raise
        else:
            return result

    async def send_friend_request(self, sender_id: int, receiver_id: int) -> None:
        if sender_id == receiver_id:
            logger.warning('User tried to send friend request to themselves: tg_id={}', sender_id)
            raise BadRequestError(detail='Cannot send friend request to yourself')
        try:
            user = await self._repository.get(sender_id)
            friend = await self._repository.get(receiver_id)
            relations = await self._repository.get_user_relations(sender_id)
            user.load_relations(relations)

            match user.resolve_friend_action(friend):
                case FriendAction.ALREADY_FRIENDS:
                    logger.warning('Users already friends: sender={}, receiver={}', sender_id, receiver_id)
                    raise BadRequestError(detail='Already friends')
                case FriendAction.ADD_FRIEND:
                    await self._repository.accept_friend_request(sender_id, receiver_id)
                    logger.success('Friends added successfully: user1={}, user2={}', sender_id, receiver_id)
                case FriendAction.REQUEST_ALREADY_SENT:
                    logger.info('Request already sent previously: sender={}, receiver={}', sender_id, receiver_id)
                    return
                case FriendAction.SEND_REQUEST:
                    await self._repository.send_friend_request(sender_id, receiver_id)
                    logger.success('Friend request sent successfully: sender={}, receiver={}', sender_id, receiver_id)
        except Exception as e:
            logger.error('Failed to send friend request from {} to {}: {}', sender_id, receiver_id, type(e).__name__)
            raise

    async def get_pending_requests(self, user_id: int) -> list[FriendRequestDTO]:
        try:
            requests = await self._repository.get_pending_requests(user_id)
            logger.success('Pending requests retrieved successfully: user_id={}, count={}', user_id, len(requests))
        except Exception as e:
            logger.error('Failed to get pending requests for user_id={}: {}', user_id, type(e).__name__)
            raise
        else:
            return requests

    async def accept_friend_request(self, receiver_id: int, sender_id: int) -> None:
        try:
            await self._repository.accept_friend_request(receiver_id, sender_id)
            logger.success('Friend request accepted successfully: sender={}, receiver={}', sender_id, receiver_id)
        except Exception as e:
            logger.error('Failed to accept friend request from {} to {}: {}', sender_id, receiver_id, type(e).__name__)
            raise

    async def reject_friend_request(self, receiver_id: int, sender_id: int) -> None:
        try:
            await self._repository.reject_friend_request(receiver_id, sender_id)
            logger.success('Friend request rejected successfully: sender={}, receiver={}', sender_id, receiver_id)
        except Exception as e:
            logger.error('Failed to reject friend request from {} to {}: {}', sender_id, receiver_id, type(e).__name__)
            raise

    async def delete_friend(self, user_id: int, friend_id: int) -> None:
        try:
            await self._repository.delete_friend(user_id, friend_id)
            logger.success('Friend deleted successfully: user={}, friend={}', user_id, friend_id)
        except Exception as e:
            logger.error('Failed to delete friend {} for user {}: {}', friend_id, user_id, type(e).__name__)
            raise

    async def get_friends(self, user_id: int) -> list[User]:
        try:
            friends = await self._repository.get_friends(user_id)
            logger.success('Friends list retrieved successfully: user_id={}, count={}', user_id, len(friends))
        except Exception as e:
            logger.error('Failed to get friends for user_id={}: {}', user_id, type(e).__name__)
            raise
        else:
            return friends
