from litestar import Controller, delete, post

from core.db import get_session
from dto.gifts import GiftCreateDTO
from services.gifts import GiftService


class GiftController(Controller):
    path = '/gifts'
    tags = ('Gifts',)

    @post(status_code=201, summary='Add gift')
    async def add(self, data: GiftCreateDTO) -> dict[str, int]:
        async with get_session() as session:
            service = GiftService(session)
            tg_id = await service.add(**data.__dict__)
            return {'tg_id': tg_id}

    @delete('/{gift_id:int}', status_code=204, summary='Delete gift')
    async def delete_gift(self, gift_id: int) -> None:
        async with get_session() as session:
            service = GiftService(session)
            await service.delete(gift_id)
