from sqlalchemy import text

from domain.users import Gift, User
from dto.users import FriendRequestDTO
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    async def add(self, obj: User) -> int:
        stmt = text("""
            INSERT INTO users (tg_id, tg_username, first_name, last_name, avatar_url, created_at, updated_at)
            VALUES (:tg_id, :tg_username, :first_name, :last_name, :avatar_url, :created_at, :updated_at)
        """)
        params = {
            'tg_id': obj.tg_id,
            'tg_username': obj.tg_username,
            'first_name': obj.first_name,
            'last_name': obj.last_name,
            'avatar_url': obj.avatar_url,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
        }
        await self._session.execute(stmt, params)
        return obj.tg_id

    async def get_friends(self, user_id: int) -> list[User]:
        query = text("""
          SELECT u.*
          FROM users u
          JOIN friends f ON f.friend_tg_id = u.tg_id
          WHERE f.user_tg_id = :tg_id
        """)
        params = {'tg_id': user_id}
        query_result = await self._session.execute(query, params)
        rows = query_result.mappings().all()

        return [User(**row) for row in rows]

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
            u.avatar_url,
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
        gifts_json = user_data.pop('gifts') or []
        gifts_list = [Gift(**g) for g in gifts_json if isinstance(g, dict)]
        user = User(**user_data)
        user.add_gifts(gifts_list)
        user.add_friends(friend_ids)

        return user

    async def send_friend_request(self, sender_id: int, receiver_id: int) -> None:
        stmt = text("""
            INSERT INTO friend_requests (sender_tg_id, receiver_tg_id, status)
            VALUES (:sender_id, :receiver_id, 'pending')
            ON CONFLICT (sender_tg_id, receiver_tg_id)
            DO UPDATE SET status = 'pending', updated_at = NOW()
        """)
        await self._session.execute(stmt, {'sender_id': sender_id, 'receiver_id': receiver_id})

    async def get_pending_requests(self, user_id: int) -> list[FriendRequestDTO]:
        stmt = text("""
            SELECT
                fr.sender_tg_id,
                fr.receiver_tg_id,
                fr.status,
                fr.created_at,
                u.first_name as sender_first_name,
                u.last_name as sender_last_name,
                u.tg_username as sender_username
            FROM friend_requests fr
            JOIN users u ON u.tg_id = fr.sender_tg_id
            WHERE fr.receiver_tg_id = :user_id AND fr.status = 'pending'
            ORDER BY fr.created_at DESC
        """)
        result = await self._session.execute(stmt, {'user_id': user_id})
        rows = result.mappings().all()

        return [
            FriendRequestDTO(
                sender_tg_id=row['sender_tg_id'],
                receiver_tg_id=row['receiver_tg_id'],
                status=row['status'],
                created_at=row['created_at'],
                sender_name=f'{row["sender_first_name"]} {row["sender_last_name"]}'
                if row['sender_last_name']
                else row['sender_first_name'],
                sender_username=row['sender_username'],
            )
            for row in rows
        ]

    async def accept_friend_request(self, receiver_id: int, sender_id: int) -> None:
        stmt_update = text("""
           UPDATE friend_requests
           SET status = 'accepted', updated_at = NOW()
           WHERE sender_tg_id = :sender_id AND receiver_tg_id = :receiver_id AND status = 'pending'
       """)
        await self._session.execute(stmt_update, {'sender_id': sender_id, 'receiver_id': receiver_id})

        stmt_friends = text("""
            INSERT INTO friends (user_tg_id, friend_tg_id)
            VALUES
                (:user1, :user2),
                (:user2, :user1)
            ON CONFLICT DO NOTHING
        """)
        await self._session.execute(stmt_friends, {'user1': sender_id, 'user2': receiver_id})

    async def reject_friend_request(self, receiver_id: int, sender_id: int) -> None:
        stmt = text("""
        UPDATE friend_requests
        SET status = 'rejected', updated_at = NOW()
        WHERE sender_tg_id = :sender_id AND receiver_tg_id = :receiver_id AND status = 'pending'
        """)
        await self._session.execute(stmt, {'sender_id': sender_id, 'receiver_id': receiver_id})

    async def delete_friend(self, user_id: int, friend_id: int) -> None:
        stmt = text("""
        DELETE FROM friends
        WHERE (user_tg_id = :user_id AND friend_tg_id = :friend_id)
        OR (user_tg_id = :friend_id AND friend_tg_id = :user_id)
        """)
        await self._session.execute(stmt, {'user_id': user_id, 'friend_id': friend_id})
