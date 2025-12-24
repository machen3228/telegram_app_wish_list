from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_user(self, user: User) -> None:
        stmt = text("""
            INSERT INTO users (tg_id, tg_username, first_name, last_name, birthday, created_at, updated_at)
            VALUES (:tg_id, :tg_username, :first_name, :last_name, :birthday, :created_at, :updated_at)
        """)
        params = {
            'tg_id': user.tg_id,
            'tg_username': user.tg_username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birthday': user.birthday,
            'created_at': user.created_at,
            'updated_at': user.updated_at,
        }
        await self._session.execute(stmt, params)
