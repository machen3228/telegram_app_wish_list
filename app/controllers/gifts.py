from litestar import Controller, delete, get, post
from litestar.dto import DataclassDTO

from core.db import get_session
from domain.users import Gift
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

    @get('/{gift_id:int}', return_dto=DataclassDTO[Gift], summary='Get gift')
    async def get(self, gift_id: int) -> Gift:
        async with get_session() as session:
            service = GiftService(session)
            return await service.get(gift_id)

    @delete('/{gift_id:int}', status_code=204, summary='Delete gift')
    async def delete_gift(self, gift_id: int) -> None:
        async with get_session() as session:
            service = GiftService(session)
            await service.delete(gift_id)
