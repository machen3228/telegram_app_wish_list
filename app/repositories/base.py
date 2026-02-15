from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository[T]:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
