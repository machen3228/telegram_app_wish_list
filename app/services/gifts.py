from sqlalchemy.ext.asyncio import AsyncSession

from domain import Gift
from exceptions.database import NotFoundInDbError
from exceptions.http import BadRequestError
from exceptions.http import ForbiddenError
from exceptions.http import NotFoundError
from repositories import GiftRepository


class GiftService:
    def __init__(self, session: AsyncSession) -> None:
        self._repository = GiftRepository(session)

    async def add(
        self,
        current_user_id: int,
        name: str,
        url: str | None,
        wish_rate: int | None,
        price: int | None,
        note: str | None,
    ) -> int:
        gift = Gift.create(
            user_id=current_user_id,
            name=name,
            url=url,
            wish_rate=wish_rate,
            price=price,
            note=note,
        )
        try:
            return await self._repository.add(gift)
        except NotFoundInDbError as e:
            raise NotFoundError(detail=str(e)) from e

    async def get(self, gift_id: int, current_user_id: int) -> Gift:
        try:
            return await self._repository.get(gift_id, current_user_id)
        except NotFoundInDbError as e:
            raise NotFoundError(detail=str(e)) from e

    async def get_gifts_by_user_id(self, tg_id: int, current_user_id: int) -> list[Gift]:
        return await self._repository.get_gifts_by_user_id(tg_id, current_user_id)

    async def delete(self, gift_id: int, current_user_id: int) -> None:
        try:
            gift = await self._repository.get(gift_id, current_user_id)
        except NotFoundInDbError as e:
            raise NotFoundError(detail=str(e)) from e
        if not gift.can_delete_gift(current_user_id):
            raise ForbiddenError(detail='You may not delete this gift')
        await self._repository.delete(gift_id)

    async def add_reservation(self, gift_id: int, current_user_id: int) -> None:
        try:
            await self._repository.get(gift_id, current_user_id)
        except NotFoundInDbError as e:
            raise NotFoundError(detail=str(e)) from e
        if not await self._repository.is_friend_or_owner(gift_id, current_user_id):
            raise ForbiddenError(detail='Not a friend or owner')
        try:
            await self._repository.add_reservation(gift_id, current_user_id)
        except NotFoundInDbError as e:
            raise NotFoundError(detail=str(e)) from e

    async def delete_reservation(self, gift_id: int, current_user_id: int) -> None:
        try:
            gift = await self._repository.get(gift_id, current_user_id)
        except NotFoundInDbError as e:
            raise NotFoundError(detail=str(e)) from e
        if not gift.is_reserved:
            raise BadRequestError(detail='The gift has no reservation')
        if not gift.can_delete_reservation(current_user_id):
            raise ForbiddenError
        await self._repository.delete_reservation(gift_id)
