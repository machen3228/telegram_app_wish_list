from litestar.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users import User
from dto.users import FriendRequestDTO
from repositories.users import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repository = UserRepository(session)

    async def add(
        self,
        tg_id: int,
        tg_username: str,
        first_name: str,
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
        except IntegrityError as e:
            raise HTTPException(status_code=400, detail='User already exists') from e
        return await self._repository.get(tg_id)

    async def get(self, tg_id: int) -> User:
        try:
            return await self._repository.get(tg_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    async def get_friends(self, user_id: int) -> list[User]:
        return await self._repository.get_friends(user_id)

    async def send_friend_request(self, sender_id: int, receiver_id: int) -> None:
        if sender_id == receiver_id:
            raise HTTPException(status_code=400, detail='Cannot send friend request to yourself')
        try:
            user = await self._repository.get(sender_id)
            friend = await self._repository.get(receiver_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail='User already in your friend list') from e
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
