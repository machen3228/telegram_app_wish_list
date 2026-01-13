from datetime import date

from litestar.exceptions import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users import User
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
        birthday: date | None,
    ) -> int:
        user = User.create(
            tg_id=tg_id,
            tg_username=tg_username,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
        )
        try:
            result = await self._repository.add(user)
        except IntegrityError:
            raise HTTPException(status_code=400, detail='User already exists') from None
        return result

    async def get(self, tg_id: int) -> User:
        try:
            return await self._repository.get(tg_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None

    async def add_friend(self, tg_id: int, friend_id: int) -> None:
        if tg_id == friend_id:
            raise HTTPException(status_code=401, detail='You can not add yourself to the friend list') from None
        try:
            friend = await self._repository.get(friend_id)
            user = await self._repository.get_user_with_friends(tg_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e)) from None
        if not user.can_add_friend(friend):
            raise HTTPException(status_code=401, detail='User already in your friend list') from None
        await self._repository.add_friend(user, friend)
