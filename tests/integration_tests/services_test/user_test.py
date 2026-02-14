from datetime import datetime

import pytest
from hamcrest import all_of, assert_that, equal_to, has_properties, instance_of
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

        assert_that(
            result,
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

    async def test_service_get_user_not_found(
        self,
        db_session: AsyncSession,
    ) -> None:
        service = UserService(db_session)
        with pytest.raises(NotFoundError, match=r'User with id=\d+ not found'):
            await service.get(123456)
