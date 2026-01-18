from sqlalchemy import text

from domain.users import Gift, User
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

    async def add_friend(self, user: User, friend: User) -> None:
        stmt = text("""
            INSERT INTO friends (user_tg_id, friend_tg_id)
            VALUES
              (:user_id, :friend_id)
            ON CONFLICT DO NOTHING;
        """)
        params = {
            'user_id': user.tg_id,
            'friend_id': friend.tg_id,
        }
        await self._session.execute(stmt, params)

    async def get(self, obj_id: int) -> User:
        query = text("""
            WITH friends_cte AS (
              SELECT
                user_tg_id,
                array_agg(friend_tg_id) AS friends_ids
              FROM friends
              GROUP BY user_tg_id
            ),
            gifts_cte AS (
              SELECT
                user_id,
                json_agg(json_build_object(
                  'id', id,
                  'user_id', user_id,
                  'name', name,
                  'url', url,
                  'wish_rate', wish_rate,
                  'price', price,
                  'note', note,
                  'created_at', created_at,
                  'updated_at', updated_at
                 )) AS gifts
              FROM gifts
              GROUP BY user_id
              )
            SELECT
              u.tg_id,
              u.tg_username,
              u.first_name,
              u.last_name,
              u.birthday,
              u.created_at,
              u.updated_at,
              COALESCE(f.friends_ids, '{}') AS friends_ids,
              COALESCE(g.gifts, '[]') AS gifts
            FROM users u
              LEFT JOIN friends_cte f ON u.tg_id = f.user_tg_id
              LEFT JOIN gifts_cte g ON u.tg_id = g.user_id
            WHERE u.tg_id = :tg_id;
        """)
        params = {'tg_id': obj_id}
        query_result = await self._session.execute(query, params)
        row = query_result.mappings().one_or_none()
        if row is None:
            raise KeyError(f'User with tg_id={obj_id} not found')
        user_data = dict(row)
        friend_ids = user_data.pop('friends_ids') or []
        gifts_json = user_data.pop('gifts') or '[]'
        gifts_list = [Gift(**g) for g in gifts_json]  # ty:ignore[invalid-argument-type]
        user = User(**user_data)
        user.add_gifts(gifts_list)
        user.add_friends(friend_ids)
        return user

    async def delete_friend(self, user: User, friend: User) -> None:
        stmt = text("""
            DELETE FROM friends WHERE user_tg_id = :tg_id AND friend_tg_id = :friend_tg_id;
        """)
        params = {'tg_id': user.tg_id, 'friend_tg_id': friend.tg_id}
        await self._session.execute(stmt, params)
