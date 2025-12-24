from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository[T](ABC):
    @abstractmethod
    async def add(self, obj: T) -> int: ...

    @abstractmethod
    async def get(self, obj_id: int) -> T: ...


class BaseRepository[T](AbstractRepository[T], ABC):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
