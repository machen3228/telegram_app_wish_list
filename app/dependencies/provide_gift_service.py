from sqlalchemy.ext.asyncio import AsyncSession

from services import GiftService


def provide_gift_service(db_session: AsyncSession) -> GiftService:
    return GiftService(db_session)
