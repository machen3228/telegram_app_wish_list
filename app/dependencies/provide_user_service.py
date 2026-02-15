from collections.abc import AsyncGenerator

from core.db import get_session
from services.users import UserService


async def provide_user_service() -> AsyncGenerator[UserService]:
    async with get_session() as session:
        yield UserService(session)
