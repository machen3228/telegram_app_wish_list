from datetime import UTC
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from domain.gifts import Gift
from exceptions.database import NotFoundInDbError
from repositories.base import BaseRepository


class GiftRepository(BaseRepository[Gift]):
    async def add(self, obj: Gift) -> int:
        stmt = text("""
            INSERT INTO gifts (user_id, name, url, wish_rate, price, note, created_at, updated_at)
            VALUES (:user_id, :name, :url, :wish_rate, :price, :note, :created_at, :updated_at)
            RETURNING id
        """)
        params = {
            'user_id': obj.user_id,
            'name': obj.name,
            'url': obj.url,
            'wish_rate': obj.wish_rate,
            'price': obj.price,
            'note': obj.note,
            'created_at': obj.created_at,
            'updated_at': obj.updated_at,
        }
        try:
            result = await self._session.execute(stmt, params)
        except IntegrityError:
            raise NotFoundInDbError('User', obj.user_id) from None
        return result.scalar_one()

    async def get(self, obj_id: int, current_user_id: int) -> Gift:
        query = text("""
          SELECT
            g.*,
            gr.gift_id IS NOT NULL AS is_reserved,
            CASE
              WHEN gr.reserved_by_tg_id = :current_user_id THEN gr.reserved_by_tg_id
              ELSE NULL
            END AS reserved_by
          FROM gifts g
          LEFT JOIN gift_reservations gr ON g.id = gr.gift_id
          WHERE g.id = :gift_id
         """)
        params = {
            'gift_id': obj_id,
            'current_user_id': current_user_id,
        }
        query_result = await self._session.execute(query, params)
        result = query_result.mappings().one_or_none()
        if result is None:
            raise NotFoundInDbError('Gift', obj_id)
        return Gift(**dict(result))

    async def get_gifts_by_user_id(self, tg_id: int, current_user_id: int) -> list[Gift]:
        query = text("""
          SELECT
            g.*,
            gr.gift_id IS NOT NULL AS is_reserved,
            CASE
              WHEN gr.reserved_by_tg_id = :current_user_id THEN gr.reserved_by_tg_id
              ELSE NULL
            END AS reserved_by
          FROM gifts g
          LEFT JOIN gift_reservations gr ON g.id = gr.gift_id
          WHERE g.user_id = :user_id
        """)
        params = {
            'user_id': tg_id,
            'current_user_id': current_user_id,
        }
        query_result = await self._session.execute(query, params)
        rows = query_result.mappings().all()
        return [Gift(**row) for row in rows]

    async def delete(self, obj_id: int) -> None:
        stmt = text("""
            DELETE FROM gifts WHERE id = :gift_id;
        """)
        params = {'gift_id': obj_id}
        await self._session.execute(stmt, params)

    async def add_reservation(self, gift_id: int, current_user_id: int) -> None:
        stmt = text("""
          INSERT INTO gift_reservations (gift_id, reserved_by_tg_id, created_at)
          VALUES (:gift_id, :reserved_by_tg_id, :created_at)
        """)
        params = {
            'gift_id': gift_id,
            'reserved_by_tg_id': current_user_id,
            'created_at': datetime.now(UTC),
        }
        await self._session.execute(stmt, params)

    async def delete_reservation_by_friend(self, gift_id: int, current_user_id: int) -> None:
        stmt = text("""
          DELETE FROM gift_reservations WHERE gift_id = :gift_id AND reserved_by_tg_id = :reserved_by_tg_id
        """)
        params = {
            'gift_id': gift_id,
            'reserved_by_tg_id': current_user_id,
        }
        await self._session.execute(stmt, params)

    async def delete_reservation_by_owner(self, gift_id: int) -> None:
        stmt = text("""
          DELETE FROM gift_reservations WHERE gift_id = :gift_id
        """)
        params = {
            'gift_id': gift_id,
        }
        await self._session.execute(stmt, params)

    async def is_friend_or_owner(self, gift_id: int, current_user_id: int) -> bool:
        query = text("""
          SELECT EXISTS (
            SELECT 1 FROM gifts g
            WHERE g.id = :gift_id
            AND (
              g.user_id = :current_user_id
              OR EXISTS (
                SELECT 1 FROM friends f
                WHERE f.user_tg_id = g.user_id
                AND f.friend_tg_id = :current_user_id
              )
            )
         )
         """)
        params = {
            'gift_id': gift_id,
            'current_user_id': current_user_id,
        }
        result = await self._session.execute(query, params)
        return result.scalar()
