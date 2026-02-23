from datetime import datetime

from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import contains_exactly
from hamcrest import contains_inanyorder
from hamcrest import equal_to
from hamcrest import greater_than
from hamcrest import has_properties
from hamcrest import instance_of
from hamcrest import none
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from domain import User
from dto.users import FriendRequestDTO
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

    async def test_repo_get_friends_success(
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
        result = await user_repository.get_friends(123)

        assert result == []

    async def test_repo_get_friends_no_friends(
        self,
        user_repository: UserRepository,
        test_user_bob: UserDict,
    ) -> None:
        result = await user_repository.get_friends(test_user_bob['tg_id'])

        assert result == []

    async def test_repo_get_user_relations_no_relations(
        self,
        user_repository: UserRepository,
        test_user_bob: UserDict,
    ) -> None:

        assert_that(
            await user_repository.get_user_relations(test_user_bob['tg_id']),
            has_properties(
                friends_ids=equal_to(set()),
                incoming_request_ids=equal_to(set()),
                outgoing_request_ids=equal_to(set()),
            ),
        )

    async def test_repo_get_user_relations_user_not_found(
        self,
        user_repository: UserRepository,
    ) -> None:
        assert_that(
            await user_repository.get_user_relations(999999),
            has_properties(
                friends_ids=equal_to(set()),
                incoming_request_ids=equal_to(set()),
                outgoing_request_ids=equal_to(set()),
            ),
        )

    async def test_repo_get_user_relations_with_friend(
        self,
        user_repository: UserRepository,
        test_user_with_friend: int,
        test_user_john: UserDict,
    ) -> None:
        assert_that(
            await user_repository.get_user_relations(test_user_with_friend),
            has_properties(
                friends_ids=contains_inanyorder(test_user_john['tg_id']),
                incoming_request_ids=equal_to(set()),
                outgoing_request_ids=equal_to(set()),
            ),
        )

    async def test_repo_get_user_relations_with_incoming_request(
        self,
        user_repository: UserRepository,
        test_user_with_incoming_request: int,
        test_user_john: UserDict,
    ) -> None:
        assert_that(
            await user_repository.get_user_relations(test_user_with_incoming_request),
            has_properties(
                friends_ids=equal_to(set()),
                incoming_request_ids=equal_to({test_user_john['tg_id']}),
                outgoing_request_ids=equal_to(set()),
            ),
        )

    async def test_repo_get_user_relations_with_outgoing_request(
        self,
        user_repository: UserRepository,
        test_user_with_outgoing_request: int,
        test_user_john: UserDict,
    ) -> None:
        assert_that(
            await user_repository.get_user_relations(test_user_with_outgoing_request),
            has_properties(
                friends_ids=equal_to(set()),
                incoming_request_ids=equal_to(set()),
                outgoing_request_ids=equal_to({test_user_john['tg_id']}),
            ),
        )

    async def test_repo_get_user_relations_rejected_not_included(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        test_user_bob: UserDict,
        test_user_john: UserDict,
    ) -> None:
        stmt = text("""
            INSERT INTO friend_requests (sender_tg_id, receiver_tg_id, status)
            VALUES (:sender_id, :receiver_id, 'rejected')
        """)
        await db_session.execute(
            stmt,
            {
                'sender_id': test_user_john['tg_id'],
                'receiver_id': test_user_bob['tg_id'],
            },
        )

        assert_that(
            await user_repository.get_user_relations(test_user_bob['tg_id']),
            has_properties(
                friends_ids=equal_to(set()),
                incoming_request_ids=equal_to(set()),
                outgoing_request_ids=equal_to(set()),
            ),
        )

    async def test_repo_get_user_relations_all_combined(
        self,
        db_session: AsyncSession,
        user_repository: UserRepository,
        test_user_bob: UserDict,
        test_user_john: UserDict,
    ) -> None:
        third_user_id = 999001
        await db_session.execute(
            text("""
                INSERT INTO users (tg_id, tg_username, first_name, created_at, updated_at)
                VALUES (:tg_id, :username, :first_name, now(), now())
            """),
            {'tg_id': third_user_id, 'username': 'third_user', 'first_name': 'Third'},
        )

        await db_session.execute(
            text("""
                INSERT INTO friends (user_tg_id, friend_tg_id)
                VALUES (:user1, :user2), (:user2, :user1)
            """),
            {'user1': test_user_bob['tg_id'], 'user2': third_user_id},
        )

        await db_session.execute(
            text("""
                INSERT INTO friend_requests (sender_tg_id, receiver_tg_id, status)
                VALUES (:sender_id, :receiver_id, 'pending')
            """),
            {'sender_id': test_user_john['tg_id'], 'receiver_id': test_user_bob['tg_id']},
        )

        assert_that(
            await user_repository.get_user_relations(test_user_bob['tg_id']),
            has_properties(
                friends_ids=contains_inanyorder(third_user_id),
                incoming_request_ids=equal_to({test_user_john['tg_id']}),
                outgoing_request_ids=equal_to(set()),
            ),
        )

    @pytest.mark.usefixtures('test_user_with_incoming_request')
    async def test_repo_get_pending_requests_success(
        self,
        user_repository: UserRepository,
        test_user_bob: UserDict,
        test_user_john: UserDict,
    ) -> None:

        assert_that(
            await user_repository.get_pending_requests(test_user_bob['tg_id']),
            contains_exactly(
                all_of(
                    instance_of(FriendRequestDTO),
                    has_properties(
                        sender_tg_id=equal_to(test_user_john['tg_id']),
                        receiver_tg_id=equal_to(test_user_bob['tg_id']),
                        status=equal_to('pending'),
                    ),
                )
            ),
        )

    async def test_repo_get_pending_requests_not_found(
        self,
        user_repository: UserRepository,
    ) -> None:
        result = await user_repository.get_pending_requests(123456)

        assert result == []
