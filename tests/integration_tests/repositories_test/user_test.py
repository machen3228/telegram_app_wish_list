from datetime import datetime

from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import greater_than
from hamcrest import has_properties
from hamcrest import instance_of
import pytest

from exceptions.database import NotFoundInDbError
from repositories import UserRepository
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
            ),
        )

    async def test_repo_get_user_not_found(
        self,
        user_repository: UserRepository,
    ) -> None:
        with pytest.raises(NotFoundInDbError, match=r'User with id=\d+ not found'):
            await user_repository.get(123456)

    async def test_repo_update_user_success(
        self,
        user_repository: UserRepository,
        test_user: UserDict,
    ) -> None:
        await user_repository.update(test_user['tg_id'], tg_username='new_username', first_name='new_first_name')
        updated_user = await user_repository.get(test_user['tg_id'])

        assert_that(
            updated_user,
            has_properties(
                tg_username=equal_to('new_username'),
                first_name=equal_to('new_first_name'),
            ),
        )

    async def test_repo_update_user_updates_updated_at(
        self,
        user_repository: UserRepository,
        test_user: UserDict,
    ) -> None:
        await user_repository.update(test_user['tg_id'], first_name='new_first_name')
        updated_user = await user_repository.get(test_user['tg_id'])

        assert_that(
            updated_user.updated_at,
            greater_than(test_user['updated_at']),
        )

    async def test_repo_update_user_does_not_change_other_fields(
        self,
        user_repository: UserRepository,
        test_user: UserDict,
    ) -> None:
        await user_repository.update(test_user['tg_id'], first_name='new_first_name')
        updated_user = await user_repository.get(test_user['tg_id'])

        assert_that(
            updated_user,
            has_properties(
                tg_username=equal_to(test_user['tg_username']),
                last_name=equal_to(test_user['last_name']),
                avatar_url=equal_to(test_user['avatar_url']),
            ),
        )

    async def test_repo_update_user_no_fields_does_nothing(
        self,
        user_repository: UserRepository,
        test_user: UserDict,
    ) -> None:
        await user_repository.update(test_user['tg_id'])
        user = await user_repository.get(test_user['tg_id'])

        assert_that(
            user,
            has_properties(
                tg_username=equal_to(test_user['tg_username']),
                first_name=equal_to(test_user['first_name']),
                updated_at=equal_to(test_user['updated_at']),
            ),
        )

    @pytest.mark.parametrize(
        ('field', 'value'),
        [
            pytest.param('tg_username', 'updated_username', id='update_tg_username'),
            pytest.param('first_name', 'updated_first_name', id='update_first_name'),
            pytest.param('last_name', 'updated_last_name', id='update_last_name'),
            pytest.param('avatar_url', 'updated_avatar_url', id='update_avatar_url'),
        ],
    )
    async def test_repo_update_user_single_field(
        self,
        user_repository: UserRepository,
        test_user: UserDict,
        field: str,
        value: str,
    ) -> None:
        await user_repository.update(test_user['tg_id'], **{field: value})
        updated_user = await user_repository.get(test_user['tg_id'])

        assert_that(updated_user, has_properties(**{field: equal_to(value)}))
