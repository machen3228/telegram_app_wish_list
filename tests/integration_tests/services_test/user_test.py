from datetime import datetime

from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_properties
from hamcrest import instance_of
from hamcrest import none
from litestar.exceptions import HTTPException
import pytest

from exceptions.http import NotFoundError
from services import UserService
from tests.integration_tests.conftest import UserDict


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserService:
    async def test_service_get_user_success(
        self,
        user_service: UserService,
        test_user: UserDict,
    ) -> None:
        assert_that(
            await user_service.get(test_user['tg_id']),
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
            ),
        )

    async def test_service_get_user_not_found(
        self,
        user_service: UserService,
    ) -> None:
        with pytest.raises(NotFoundError, match=r'User with id=\d+ not found'):
            await user_service.get(123456)

    async def test_service_add_user_success(
        self,
        user_service: UserService,
    ) -> None:
        result = await user_service.add(
            tg_id=999999,
            tg_username='new_user',
            first_name='New',
            last_name='User',
            avatar_url='https://avatar.jpg',
        )

        assert_that(
            result,
            has_properties(
                tg_id=equal_to(999999),
                tg_username=equal_to('new_user'),
                first_name=equal_to('New'),
                last_name=equal_to('User'),
                avatar_url=equal_to('https://avatar.jpg'),
                created_at=instance_of(datetime),
                updated_at=instance_of(datetime),
            ),
        )

    async def test_service_add_user_with_nullable_fields(
        self,
        user_service: UserService,
    ) -> None:
        result = await user_service.add(
            tg_id=999998,
            tg_username=None,
            first_name=None,
            last_name=None,
            avatar_url=None,
        )

        assert_that(
            result,
            has_properties(
                tg_username=none(),
                first_name=none(),
                last_name=none(),
                avatar_url=none(),
            ),
        )

    async def test_service_add_user_duplicate_raises_http_exception(
        self,
        user_service: UserService,
        test_user: UserDict,
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await user_service.add(
                tg_id=test_user['tg_id'],
                tg_username='another_username',
                first_name='Another',
                last_name=None,
                avatar_url=None,
            )

        assert_that(
            exc_info.value,
            has_properties(
                status_code=equal_to(400),
                detail=equal_to("User with this 'tg_id' already exists"),
            ),
        )
