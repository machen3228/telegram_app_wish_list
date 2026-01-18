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
        pass
