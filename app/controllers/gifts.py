from litestar import Controller, delete, get, post
from litestar.di import Provide

from core.db import get_session
from core.security.jwt_auth import AccessJWTAuth
from domain.gifts import Gift
from dto.gifts import GiftCreateDTO
from services.gifts import GiftService


class GiftController(Controller):
    path = '/gifts'
    tags = ('Gifts',)

    @post(
        status_code=201,
        summary='Add gift',
        dependencies={'current_user_id': Provide(AccessJWTAuth)},
    )
    async def add(self, data: GiftCreateDTO, current_user_id: int) -> dict[str, int]:
        async with get_session() as session:
            service = GiftService(session)
            tg_id = await service.add(current_user_id, **data.__dict__)
            return {'tg_id': tg_id}

    @delete(
        '/{gift_id:int}',
        status_code=204,
        summary='Delete gift',
        dependencies={'current_user_id': Provide(AccessJWTAuth)},
    )
    async def delete_gift(self, gift_id: int, current_user_id: int) -> None:
        async with get_session() as session:
            service = GiftService(session)
            await service.delete(gift_id, current_user_id)

    @post(
        '/{gift_id:int}/reserve',
        status_code=201,
        summary='Add gift reservation',
        dependencies={'current_user_id': Provide(AccessJWTAuth)},
    )
    async def add_reservation(self, gift_id: int, current_user_id: int) -> None:
        async with get_session() as session:
            service = GiftService(session)
            await service.add_reservation(gift_id, current_user_id)

    @delete(
        '/{gift_id:int}/reserve/friend',
        status_code=204,
        summary='Withdraw reservation by friend',
        dependencies={'current_user_id': Provide(AccessJWTAuth)},
    )
    async def delete_reservation_by_friend(self, gift_id: int, current_user_id: int) -> None:
        async with get_session() as session:
            service = GiftService(session)
            await service.delete_reservation_by_friend(gift_id, current_user_id)

    @delete(
        '/{gift_id:int}/reserve/owner',
        status_code=204,
        summary='Withdraw reservation by owner',
        dependencies={'current_user_id': Provide(AccessJWTAuth)},
    )
    async def delete_reservation_by_owner(self, gift_id: int, current_user_id: int) -> None:
        async with get_session() as session:
            service = GiftService(session)
            await service.delete_reservation_by_owner(gift_id, current_user_id)

    @get(
        '/user/{tg_id:int}',
        summary='Get user wishlist',
        dependencies={'current_user_id': Provide(AccessJWTAuth)},
    )
    async def get_user_gifts(
        self,
        tg_id: int,
        current_user_id: int,
    ) -> list[Gift]:
        async with get_session() as session:
            service = GiftService(session)
            return await service.get_gifts_by_user_id(tg_id, current_user_id)
