from sqlalchemy import text

from domain.users import Gift
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
        result = await self._session.execute(stmt, params)
        return result.scalar_one()

    async def get(self, obj_id: int) -> Gift:
        query = text("""
            SELECT *
            FROM gifts g
            WHERE g.id = :gift_id
         """)
        params = {'gift_id': obj_id}
        query_result = await self._session.execute(query, params)
        result = query_result.mappings().one_or_none()
        if result is None:
            raise KeyError(f'Gift with id={obj_id} not found')
        return Gift(**dict(result))

    async def get_gifts_by_user_id(self, tg_id: int) -> list[Gift]:
        query = text("""
          SELECT *
          FROM gifts g
          WHERE g.user_id = :user_id
        """)
        params = {'user_id': tg_id}
        query_result = await self._session.execute(query, params)
        rows = query_result.mappings().all()
        return [Gift(**row) for row in rows]

    async def delete(self, obj_id: int) -> None:
        stmt = text("""
            DELETE FROM gifts WHERE id = :gift_id;
        """)
        params = {'gift_id': obj_id}
        await self._session.execute(stmt, params)
