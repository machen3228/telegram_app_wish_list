import pytest
from integration_tests.conftest import UserDict
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.users import UserRepository


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserRepository:
    async def test_get_user(
        self,
        db_session: AsyncSession,
        test_user: UserDict,
    ) -> None:
        repo = UserRepository(db_session)
        result = await repo.get(test_user['tg_id'])

        assert result.tg_id == test_user['tg_id']
