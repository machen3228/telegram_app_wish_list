from sqlalchemy import text

from domain.users import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    async def add(self, obj: User) -> int:
        stmt = text("""
            INSERT INTO users (tg_id, tg_username, first_name, last_name, birthday, created_at, updated_at)
            VALUES (:tg_id, :tg_username, :first_name, :last_name, :birthday, :created_at, :updated_at)
        """)
        params = {
            'tg_id': obj.tg_id,
            'tg_username': obj.tg_username,
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'birthday': obj.birthday,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
        }
        await self._session.execute(stmt, params)
        return obj.tg_id

    async def get(self, obj_id: int) -> User:
        query = text("""
            SELECT tg_id, tg_username, first_name, last_name, birthday, created_at, updated_at
            FROM users
            WHERE tg_id = :tg_id
        """)
        params = {'tg_id': obj_id}
        query_result = await self._session.execute(query, params)
        row = query_result.mappings().one_or_none()
        if row is None:
            raise KeyError(f'User with tg_id={obj_id} not found')
        user_data = dict(row)
        return User(**user_data)

    async def add_friend(self, user: User, friend: User) -> None:
        stmt = text("""
            INSERT INTO friends (user_tg_id, friend_tg_id)
            VALUES
                (:user_id, :friend_id),
                (:friend_id, :user_id)
            ON CONFLICT DO NOTHING;
        """)
        params = {
            'user_id': user.tg_id,
            'friend_id': friend.tg_id,
        }
        await self._session.execute(stmt, params)

    async def get_user_with_friends(self, tg_id: int) -> User:
        query = text("""
            SELECT
                u.tg_id,
                u.tg_username,
                u.first_name,
                u.last_name,
                u.birthday,
                u.created_at,
                u.updated_at,
                array_agg(f.friend_tg_id) FILTER (WHERE f.friend_tg_id IS NOT NULL) AS _friends
            FROM users u
            LEFT JOIN friends f ON u.tg_id = f.user_tg_id
            WHERE u.tg_id = :tg_id
            GROUP BY u.tg_id
        """)
        params = {'tg_id': tg_id}
        query_result = await self._session.execute(query, params)
        row = query_result.mappings().one_or_none()
        if row is None:
            raise KeyError(f'User with tg_id={tg_id} not found')
        user_data = dict(row)
        user_data['_friends'] = user_data['_friends'] or []
        return User(**user_data)
