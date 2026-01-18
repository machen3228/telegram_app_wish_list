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
