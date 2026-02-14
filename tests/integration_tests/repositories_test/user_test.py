from datetime import datetime

import pytest
from hamcrest import all_of, assert_that, equal_to, has_properties, instance_of

from exceptions.database import NotFoundInDbError
from repositories.users import UserRepository
from tests.integration_tests.conftest import UserDict


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserRepository:
    async def test_repo_get_user_success(
        self,
        user_repository: UserRepository,
        test_user: UserDict,
    ) -> None:
        assert_that(
            await user_repository.get(test_user['tg_id']),
            has_properties(
                tg_id=all_of(
                    instance_of(int),
                    equal_to(test_user['tg_id']),
                ),
                tg_username=instance_of(str),
                first_name=instance_of(str),
                last_name=instance_of(str),
                avatar_url=instance_of(str),
                created_at=instance_of(datetime),
                updated_at=instance_of(datetime),
            )
        )

    async def test_repo_get_user_not_found(
        self,
        user_repository: UserRepository,
    ) -> None:
        with pytest.raises(NotFoundInDbError, match=r'User with id=\d+ not found'):
            await user_repository.get(123456)
