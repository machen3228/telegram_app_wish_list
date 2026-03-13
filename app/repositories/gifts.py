from datetime import UTC
from datetime import datetime

from loguru import logger
from sqlalchemy import TextClause
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from domain.gifts import Gift
from exceptions.database import NotFoundInDbError
from repositories.base import BaseRepository
from utils import handle_integrity_error_message


def _gift_select_query(where_clause: str) -> TextClause:
    return text(f"""
        SELECT
            g.*,
            gr.gift_id IS NOT NULL AS is_reserved,
            CASE
                WHEN gr.reserved_by_tg_id = :current_user_id THEN gr.reserved_by_tg_id
                ELSE NULL
            END AS reserved_by
        FROM gifts g
        LEFT JOIN gift_reservations gr ON g.id = gr.gift_id
        WHERE {where_clause}
    """)


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
            await self._session.commit()
        except IntegrityError as e:
            context = {'user_id': obj.user_id}
            message = handle_integrity_error_message(e, context)
            logger.critical('Failed to add gift: IntegrityError for user_id={}: {}', obj.user_id, message)
            raise NotFoundInDbError(message) from None
        return result.scalar_one()

    async def get(self, obj_id: int, current_user_id: int) -> Gift:
        query = _gift_select_query('g.id = :gift_id')
        params = {'gift_id': obj_id, 'current_user_id': current_user_id}
        try:
            result = await self._session.execute(query, params)
            row = result.mappings().one_or_none()
        except Exception as e:
            logger.error('Failed to get gift with id={}: {}', obj_id, type(e).__name__)
            raise

        if row is None:
            logger.warning('Gift with id={} not found', obj_id)
            raise NotFoundInDbError(f'Gift with id={obj_id} not found')
        return Gift(**row)

    async def get_gifts_by_user_id(self, tg_id: int, current_user_id: int) -> list[Gift]:
        query = _gift_select_query('g.user_id = :user_id')
        params = {'user_id': tg_id, 'current_user_id': current_user_id}
        try:
            result = await self._session.execute(query, params)
            gifts = [Gift(**row) for row in result.mappings()]
        except Exception as e:
            logger.error('Failed to get gifts for user_id={}: {}', tg_id, type(e).__name__)
            raise
        return gifts

    async def get_my_reservations(self, current_user_id: int) -> list[Gift]:
        query = _gift_select_query('gr.reserved_by_tg_id = :current_user_id')
        params = {'current_user_id': current_user_id}
        try:
            result = await self._session.execute(query, params)
            gifts = [Gift(**row) for row in result.mappings()]
        except Exception as e:
            logger.error('Failed to get reservations for user_id={}: {}', current_user_id, type(e).__name__)
            raise
        return gifts

    async def delete(self, obj_id: int) -> None:
        stmt = text("""
            DELETE FROM gifts WHERE id = :gift_id;
        """)
        params = {'gift_id': obj_id}
        try:
            await self._session.execute(stmt, params)
            await self._session.commit()
        except Exception as e:
            logger.error('Failed to delete gift with id={}: {}', obj_id, type(e).__name__)
            raise

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
        try:
            await self._session.execute(stmt, params)
            await self._session.commit()
        except IntegrityError as e:
            context = {
                'gift_id': gift_id,
                'reserved_by_tg_id': current_user_id,
            }
            message = handle_integrity_error_message(e, context)
            logger.critical('Failed to add reservation: IntegrityError for gift_id={}: {}', gift_id, message)
            raise NotFoundInDbError(message) from None
        except Exception as e:
            logger.error('Failed to add reservation for gift_id={}: {}', gift_id, type(e).__name__)
            raise

    async def delete_reservation(self, gift_id: int) -> None:
        stmt = text("""
          DELETE FROM gift_reservations WHERE gift_id = :gift_id
        """)
        params = {'gift_id': gift_id}
        try:
            await self._session.execute(stmt, params)
            await self._session.commit()
        except Exception as e:
            logger.error('Failed to delete reservation for gift_id={}: {}', gift_id, type(e).__name__)
            raise

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
        try:
            result = await self._session.execute(query, params)
            await self._session.commit()
            return result.scalar()
        except Exception as e:
            logger.error('Failed to check if user is friend or owner for gift_id={}: {}', gift_id, type(e).__name__)
            raise
