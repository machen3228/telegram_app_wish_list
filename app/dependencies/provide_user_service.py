from sqlalchemy.ext.asyncio import AsyncSession

from services import UserService


async def provide_user_service(db_session: AsyncSession) -> UserService:  # TODO: make sync
    return UserService(db_session)
