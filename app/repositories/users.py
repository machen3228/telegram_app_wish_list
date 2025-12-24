from sqlalchemy import text

from domain.users import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    async def add(self, user: User) -> int:
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
        return user.tg_id

    async def get(self, tg_id: int) -> User:
        query = text("""
            SELECT tg_id, tg_username, first_name, last_name, birthday, created_at, updated_at
            FROM users
            WHERE tg_id = :tg_id
        """)
        params = {'tg_id': tg_id}
        query_result = await self._session.execute(query, params)
        row = query_result.mappings().one_or_none()
        if row is None:
            raise KeyError
        return User(**row)
