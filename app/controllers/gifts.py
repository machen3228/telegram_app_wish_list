from litestar import Controller
from litestar import delete
from litestar import get
from litestar import post
from litestar.di import Provide

from dependencies import provide_access_jwt_auth
from dependencies import provide_gift_service
from domain.gifts import Gift
from dto.gifts import GiftCreateDTO
from services import GiftService


class GiftController(Controller):
    path = '/gifts'
    tags = ('Gifts',)
    dependencies = {'service': Provide(provide_gift_service, sync_to_thread=False)}

    @post(
        status_code=201,
        summary='Add gift',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def add(
        self,
        service: GiftService,
        data: GiftCreateDTO,
        current_user_id: int,
    ) -> dict[str, int]:
        tg_id = await service.add(current_user_id, **data.__dict__)
        return {'tg_id': tg_id}

    @delete(
        '/{gift_id:int}',
        status_code=204,
        summary='Delete gift',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def delete_gift(
        self,
        service: GiftService,
        gift_id: int,
        current_user_id: int,
    ) -> None:
        await service.delete(gift_id, current_user_id)

    @post(
        '/{gift_id:int}/reserve',
        status_code=201,
        summary='Add gift reservation',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def add_reservation(
        self,
        service: GiftService,
        gift_id: int,
        current_user_id: int,
    ) -> None:
        await service.add_reservation(gift_id, current_user_id)

    @delete(
        '/{gift_id:int}/reserve/friend',
        status_code=204,
        summary='Withdraw reservation by friend',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def delete_reservation_by_friend(
        self,
        service: GiftService,
        gift_id: int,
        current_user_id: int,
    ) -> None:
        await service.delete_reservation_by_friend(gift_id, current_user_id)

    @delete(
        '/{gift_id:int}/reserve/owner',
        status_code=204,
        summary='Withdraw reservation by owner',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def delete_reservation_by_owner(
        self,
        service: GiftService,
        gift_id: int,
        current_user_id: int,
    ) -> None:
        await service.delete_reservation_by_owner(gift_id, current_user_id)

    @get(
        '/user/{tg_id:int}',
        summary='Get user wishlist',
        dependencies={'current_user_id': Provide(provide_access_jwt_auth)},
    )
    async def get_user_gifts(
        self,
        service: GiftService,
        tg_id: int,
        current_user_id: int,
    ) -> list[Gift]:
        return await service.get_gifts_by_user_id(tg_id, current_user_id)
