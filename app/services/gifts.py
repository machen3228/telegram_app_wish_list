from litestar.exceptions import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from domain.users import Gift
from repositories.gifts import GiftRepository


class GiftService:
    def __init__(self, session: AsyncSession) -> None:
        self._repository = GiftRepository(session)

    async def add(
        self,
        user_id: int,
        name: str,
        url: str | None,
        wish_rate: int | None,
        price: int | None,
        note: str | None,
    ) -> int:
        gift = Gift.create(
            user_id=user_id,
            name=name,
            url=url,
            wish_rate=wish_rate,
            price=price,
            note=note,
        )
        return await self._repository.add(gift)

    async def get(self, gift_id: int) -> Gift:
        try:
            return await self._repository.get(gift_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

    async def get_gifts_by_user_id(self, tg_id: int) -> list[Gift]:
        return await self._repository.get_gifts_by_user_id(tg_id)

    async def delete(self, gift_id: int) -> None:
        try:
            await self._repository.get(gift_id)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e
        return await self._repository.delete(gift_id)
