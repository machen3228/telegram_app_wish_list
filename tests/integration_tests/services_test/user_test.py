import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.http import NotFoundError
from services.users import UserService
from tests.integration_tests.conftest import UserDict


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserService:
    async def test_service_get_user_success(
        self,
        db_session: AsyncSession,
        test_user: UserDict,
    ) -> None:
        service = UserService(db_session)
        result = await service.get(test_user['tg_id'])

        assert result.tg_id == test_user['tg_id']

    async def test_service_get_user_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        service = UserService(db_session)
        with pytest.raises(NotFoundError, match=r'User with id=\d+ not found'):
            await service.get(123456)
