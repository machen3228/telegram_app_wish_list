from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from domain.users import User
from repositories.users import UserRepository


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._repository = UserRepository(session)

    async def create_user(
        self,
        tg_id: int,
        tg_username: str,
        first_name: str,
        last_name: str | None,
        birthday: date | None,
    ) -> User:
        user = User.create(
            tg_id=tg_id,
            tg_username=tg_username,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
        )
        await self._repository.create_user(user)
        return user
