from sqlalchemy.ext.asyncio import AsyncSession

from services import GiftService


async def provide_gift_service(db_session: AsyncSession) -> GiftService:  # TODO: make sync
    return GiftService(db_session)
