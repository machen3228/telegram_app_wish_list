from sqlalchemy.ext.asyncio import AsyncSession

from services.users import UserService


async def provide_user_service(db_session: AsyncSession) -> UserService:
    return UserService(db_session)
