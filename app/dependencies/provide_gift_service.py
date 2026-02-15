from sqlalchemy.ext.asyncio import AsyncSession

from services.gifts import GiftService


async def provide_gift_service(db_session: AsyncSession) -> GiftService:
    return GiftService(db_session)
