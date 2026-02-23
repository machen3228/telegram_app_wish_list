from datetime import datetime

from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import contains_exactly
from hamcrest import equal_to
from hamcrest import has_entries
from hamcrest import has_properties
from hamcrest import instance_of
from hamcrest import none
from litestar.exceptions import HTTPException
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from core.security import TelegramInitData
from core.security import TokenOut
from dto.users import FriendRequestDTO
from exceptions.http import BadRequestError
from exceptions.http import NotFoundError
from services import UserService
from tests.integration_tests.conftest import UserDict


@pytest.mark.integration
@pytest.mark.asyncio
class TestUserService:
    async def test_service_get_user_success(
        self,
        user_service: UserService,
        test_user_bob: UserDict,
    ) -> None:
        assert_that(
            await user_service.get(test_user_bob['tg_id']),
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
        test_user_bob: UserDict,
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await user_service.add(
                tg_id=test_user_bob['tg_id'],
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

    async def test_service_telegram_login_new_user_success(
        self,
        user_service: UserService,
    ) -> None:
        init_data: TelegramInitData = {
            'id': 999999,
            'first_name': 'John',
            'username': 'john',
            'last_name': 'Doe',
            'photo_url': 'https://avatar.jpg',
        }

        assert_that(await user_service.telegram_login(init_data), instance_of(TokenOut))

    async def test_service_telegram_login_new_user_is_saved(
        self,
        user_service: UserService,
    ) -> None:
        init_data: TelegramInitData = {
            'id': 999999,
            'first_name': 'John',
            'username': 'john',
            'last_name': 'Doe',
            'photo_url': 'https://avatar.jpg',
        }
        await user_service.telegram_login(init_data)

        assert_that(
            await user_service.get(init_data['id']),
            has_properties(
                tg_id=equal_to(init_data['id']),
                tg_username=equal_to(init_data['username']),
                first_name=equal_to(init_data['first_name']),
                last_name=equal_to(init_data['last_name']),
                avatar_url=equal_to(init_data['photo_url']),
            ),
        )

    async def test_service_telegram_login_existing_user_success(
        self,
        user_service: UserService,
        test_user_bob: UserDict,
    ) -> None:
        init_data: TelegramInitData = {
            'id': test_user_bob['tg_id'],
            'first_name': test_user_bob['first_name'],
            'username': test_user_bob['tg_username'],
        }

        assert_that(await user_service.telegram_login(init_data), instance_of(TokenOut))

    async def test_service_telegram_login_existing_user_updates_changed_fields(
        self,
        user_service: UserService,
        test_user_bob: UserDict,
    ) -> None:
        init_data: TelegramInitData = {
            'id': test_user_bob['tg_id'],
            'first_name': 'UpdatedName',
            'username': 'updated_username',
        }
        await user_service.telegram_login(init_data)

        assert_that(
            await user_service.get(test_user_bob['tg_id']),
            has_properties(
                tg_username=equal_to('updated_username'),
                first_name=equal_to('UpdatedName'),
            ),
        )

    async def test_service_send_friend_request_self_request_raises(
        self,
        user_service: UserService,
        test_user_bob: UserDict,
    ) -> None:
        with pytest.raises(BadRequestError, match='Cannot send friend request to yourself'):
            await user_service.send_friend_request(
                sender_id=test_user_bob['tg_id'],
                receiver_id=test_user_bob['tg_id'],
            )

    async def test_service_send_friend_request_sender_not_found_raises(
        self,
        user_service: UserService,
        test_user_bob: UserDict,
    ) -> None:
        with pytest.raises(NotFoundError):
            await user_service.send_friend_request(
                sender_id=999999,
                receiver_id=test_user_bob['tg_id'],
            )

    async def test_service_send_friend_request_receiver_not_found_raises(
        self,
        user_service: UserService,
        test_user_bob: UserDict,
    ) -> None:
        with pytest.raises(NotFoundError):
            await user_service.send_friend_request(
                sender_id=test_user_bob['tg_id'],
                receiver_id=999999,
            )

    async def test_service_send_friend_request_already_friends_raises(
        self,
        user_service: UserService,
        test_user_with_friend: int,
        test_user_john: UserDict,
    ) -> None:
        with pytest.raises(BadRequestError, match='Already friends'):
            await user_service.send_friend_request(
                sender_id=test_user_with_friend,
                receiver_id=test_user_john['tg_id'],
            )

    async def test_service_send_friend_request_success(
        self,
        db_session: AsyncSession,
        user_service: UserService,
        test_user_bob: UserDict,
        test_user_john: UserDict,
    ) -> None:
        await user_service.send_friend_request(
            sender_id=test_user_bob['tg_id'],
            receiver_id=test_user_john['tg_id'],
        )

        result = await db_session.execute(
            text("""
                SELECT status
                FROM friend_requests
                WHERE sender_tg_id = :sender_id AND receiver_tg_id = :receiver_id
            """),
            {'sender_id': test_user_bob['tg_id'], 'receiver_id': test_user_john['tg_id']},
        )

        assert_that(result.mappings().first(), has_entries(status=equal_to('pending')))  # ty:ignore[no-matching-overload]

    async def test_service_send_friend_request_duplicate_does_not_raise(
        self,
        user_service: UserService,
        test_user_with_outgoing_request: int,
        test_user_john: UserDict,
    ) -> None:
        await user_service.send_friend_request(
            sender_id=test_user_with_outgoing_request,
            receiver_id=test_user_john['tg_id'],
        )

    async def test_service_send_friend_request_mutual_creates_friendship(
        self,
        db_session: AsyncSession,
        user_service: UserService,
        test_user_with_incoming_request: int,
        test_user_john: UserDict,
    ) -> None:
        await user_service.send_friend_request(
            sender_id=test_user_with_incoming_request,
            receiver_id=test_user_john['tg_id'],
        )

        result = await db_session.execute(
            text("""
            SELECT COUNT(*) as cnt
            FROM friends
            WHERE (user_tg_id = :user1 AND friend_tg_id = :user2)
               OR (user_tg_id = :user2 AND friend_tg_id = :user1)
            """),
            {'user1': test_user_with_incoming_request, 'user2': test_user_john['tg_id']},
        )
        row = result.mappings().first()

        assert_that(row, has_entries(cnt=equal_to(2)))  # ty:ignore[no-matching-overload]

    @pytest.mark.usefixtures('test_user_with_incoming_request')
    async def test_service_get_pending_requests_success(
        self,
        user_service: UserService,
        test_user_bob: UserDict,
        test_user_john: UserDict,
    ) -> None:
        assert_that(
            await user_service.get_pending_requests(test_user_bob['tg_id']),
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

    async def test_service_get_pending_requests_not_found(
        self,
        user_service: UserService,
    ) -> None:
        result = await user_service.get_pending_requests(123456)

        assert result == []
