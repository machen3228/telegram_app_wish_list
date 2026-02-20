from litestar.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import BaseJWTAuth
from core.security import TelegramInitData
from core.security import TokenOut
from domain import User
from dto.users import FriendRequestDTO
from exceptions.database import AlreadyExistsInDbError
from exceptions.database import NotFoundInDbError
from exceptions.http import NotFoundError
from repositories import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repository = UserRepository(session)

    async def telegram_login(self, init_data: TelegramInitData) -> TokenOut:
        try:
            user = await self._repository.get(init_data['id'])
            fields_to_update = user.get_changed_fields(init_data)
            if fields_to_update:
                await self._repository.update(init_data['id'], **fields_to_update)
        except NotFoundInDbError:
            await self.add(
                tg_id=init_data['id'],
                tg_username=init_data.get('username', ''),
                first_name=init_data.get('first_name', ''),
                last_name=init_data.get('last_name', ''),
                avatar_url=init_data.get('photo_url', ''),
            )
        return BaseJWTAuth.create_token(init_data['id'])

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
        except AlreadyExistsInDbError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        return await self._repository.get(tg_id)

    async def get(self, tg_id: int) -> User:
        try:
            return await self._repository.get(tg_id)
        except NotFoundInDbError as e:
            raise NotFoundError(detail=str(e)) from e

    async def get_friends(self, user_id: int) -> list[User]:
        return await self._repository.get_friends(user_id)

    async def send_friend_request(self, sender_id: int, receiver_id: int) -> None:
        if sender_id == receiver_id:
            raise HTTPException(status_code=400, detail='Cannot send friend request to yourself')
        try:
            user = await self._repository.get(sender_id)
            friend = await self._repository.get(receiver_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        if not user.can_add_friend(friend):
            raise HTTPException(status_code=400, detail='Already friends') from None
        await self._repository.send_friend_request(sender_id, receiver_id)

    async def get_pending_requests(self, user_id: int) -> list[FriendRequestDTO]:
        return await self._repository.get_pending_requests(user_id)

    async def accept_friend_request(self, receiver_id: int, sender_id: int) -> None:
        await self._repository.accept_friend_request(receiver_id, sender_id)

    async def reject_friend_request(self, receiver_id: int, sender_id: int) -> None:
        await self._repository.reject_friend_request(receiver_id, sender_id)

    async def delete_friend(self, user_id: int, friend_id: int) -> None:
        await self._repository.delete_friend(user_id, friend_id)
