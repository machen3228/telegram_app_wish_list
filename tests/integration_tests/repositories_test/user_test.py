import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.database import NotFoundInDbError
from repositories.users import UserRepository
from tests.integration_tests.conftest import UserDict


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserRepository:
    async def test_repo_get_user_success(
        self,
        db_session: AsyncSession,
        test_user: UserDict,
    ) -> None:
        repo = UserRepository(db_session)
        result = await repo.get(test_user['tg_id'])

        assert result.tg_id == test_user['tg_id']

    async def test_repo_get_user_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        repo = UserRepository(db_session)
        with pytest.raises(NotFoundInDbError, match=r'User with id=\d+ not found'):
            await repo.get(123456)
