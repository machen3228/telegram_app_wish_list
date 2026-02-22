from datetime import datetime

from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import greater_than
from hamcrest import has_properties
from hamcrest import instance_of
from hamcrest import none
import pytest

from domain import User
from exceptions.database import AlreadyExistsInDbError
from exceptions.database import NotFoundInDbError
from repositories import UserRepository
from tests.integration_tests.conftest import UserDict


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserRepository:
    async def test_repo_get_user_success(
        self,
        user_repository: UserRepository,
        test_user_bob: UserDict,
    ) -> None:
        assert_that(
            await user_repository.get(test_user_bob['tg_id']),
            has_properties(
                tg_id=all_of(
                    instance_of(int),
                    equal_to(test_user_bob['tg_id']),
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
        test_user_bob: UserDict,
    ) -> None:
        await user_repository.update(test_user_bob['tg_id'], tg_username='new_username', first_name='new_first_name')

        assert_that(
            await user_repository.get(test_user_bob['tg_id']),
            has_properties(
                tg_username=equal_to('new_username'),
                first_name=equal_to('new_first_name'),
                last_name=equal_to(test_user_bob['last_name']),
                avatar_url=equal_to(test_user_bob['avatar_url']),
                updated_at=greater_than(test_user_bob['updated_at']),
            ),
        )

    async def test_repo_update_user_no_fields_does_nothing(
        self,
        user_repository: UserRepository,
        test_user_bob: UserDict,
    ) -> None:
        await user_repository.update(test_user_bob['tg_id'])
        user = await user_repository.get(test_user_bob['tg_id'])

        assert_that(
            user,
            has_properties(
                tg_username=equal_to(test_user_bob['tg_username']),
                first_name=equal_to(test_user_bob['first_name']),
                updated_at=equal_to(test_user_bob['updated_at']),
            ),
        )

    async def test_repo_add_user_success(
        self,
        user_repository: UserRepository,
    ) -> None:
        user = User.create(
            tg_id=999999,
            tg_username='new_user',
            first_name='New',
            last_name='User',
            avatar_url='https://avatar.jpg',
        )

        assert_that(await user_repository.add(user), equal_to(user.tg_id))
        assert_that(
            await user_repository.get(user.tg_id),
            has_properties(
                tg_id=equal_to(user.tg_id),
                tg_username=equal_to(user.tg_username),
                first_name=equal_to(user.first_name),
                last_name=equal_to(user.last_name),
                avatar_url=equal_to(user.avatar_url),
            ),
        )

    async def test_repo_add_user_with_nullable_fields(
        self,
        user_repository: UserRepository,
    ) -> None:
        user = User.create(
            tg_id=999998,
            tg_username=None,
            first_name=None,
            last_name=None,
            avatar_url=None,
        )
        await user_repository.add(user)

        assert_that(
            await user_repository.get(user.tg_id),
            has_properties(
                tg_username=none(),
                first_name=none(),
                last_name=none(),
                avatar_url=none(),
            ),
        )

    async def test_repo_add_user_duplicate_tg_id_raises(
        self,
        user_repository: UserRepository,
        test_user_bob: UserDict,
    ) -> None:
        user = User.create(
            tg_id=test_user_bob['tg_id'],
            tg_username='another_username',
            first_name='Another',
            last_name=None,
            avatar_url=None,
        )

        with pytest.raises(AlreadyExistsInDbError, match=r"User with this 'tg_id' already exists"):
            await user_repository.add(user)

    async def test_repo_add_user_duplicate_tg_username_raises(
        self,
        user_repository: UserRepository,
        test_user_bob: UserDict,
    ) -> None:
        user = User.create(
            tg_id=999997,
            tg_username=test_user_bob['tg_username'],
            first_name='Another',
            last_name=None,
            avatar_url=None,
        )

        with pytest.raises(AlreadyExistsInDbError, match=r"User with this 'tg_username' already exists"):
            await user_repository.add(user)

    async def test_repo_get_friends_short_success(
        self,
        user_repository: UserRepository,
        test_user_with_friend: int,
        test_user_john: UserDict,
    ) -> None:
        result = await user_repository.get_friends(test_user_with_friend, return_type='short')

        assert result == [test_user_john['tg_id']]

    async def test_repo_get_friends_full_success(
        self,
        user_repository: UserRepository,
        test_user_with_friend: int,
        test_user_john: UserDict,
    ) -> None:
        result = await user_repository.get_friends(test_user_with_friend, return_type='full')

        assert result == [User(**test_user_john)]

    async def test_repo_get_friends_default_success(
        self,
        user_repository: UserRepository,
        test_user_with_friend: int,
        test_user_john: UserDict,
    ) -> None:
        result = await user_repository.get_friends(test_user_with_friend)

        assert result == [User(**test_user_john)]

    async def test_repo_get_friends_user_not_found(
        self,
        user_repository: UserRepository,
    ) -> None:
        result = await user_repository.get_friends(123, return_type='short')

        assert result == []

    async def test_repo_get_friends_no_friends(
        self,
        user_repository: UserRepository,
        test_user_bob: UserDict,
    ) -> None:
        result = await user_repository.get_friends(test_user_bob['tg_id'], return_type='short')

        assert result == []
