from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_properties
from hamcrest import is_
from hamcrest import none
from hamcrest import not_none
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from domain import Gift
from exceptions.database import NotFoundInDbError
from repositories import GiftRepository
from tests.integration_tests.conftest import GiftDict
from tests.integration_tests.conftest import UserDict


@pytest.mark.integration
@pytest.mark.asyncio
class TestGiftRepository:
    async def test_repo_add_gift_success(
        self,
        db_session: AsyncSession,
        gift_repository: GiftRepository,
        test_user_bob: UserDict,
        gift_data: dict,
    ) -> None:
        gift = Gift.create(**gift_data, user_id=test_user_bob['tg_id'])
        gift_id = await gift_repository.add(gift)

        query = await db_session.execute(
            text("""
                SELECT *
                FROM gifts
                WHERE id = :gift_id
            """),
            {'gift_id': gift_id},
        )

        assert_that(
            query.mappings().first(),
            has_properties(
                user_id=equal_to(test_user_bob['tg_id']),
                name=equal_to('Plane'),
                url=equal_to('https://www.google.com/'),
                wish_rate=equal_to(10),
                price=equal_to(1_000_000),
                note=equal_to('white'),
                created_at=not_none(),
                updated_at=not_none(),
            ),
        )

    async def test_repo_add_gift_user_not_found(
        self,
        gift_repository: GiftRepository,
        gift_data: dict,
    ) -> None:
        gift = Gift.create(**gift_data, user_id=123456)

        with pytest.raises(NotFoundInDbError, match='User with id=123456 not found'):
            await gift_repository.add(gift)

    async def test_repo_delete_gift_success(
        self,
        db_session: AsyncSession,
        gift_repository: GiftRepository,
        test_bob_gift: GiftDict,
    ) -> None:
        await gift_repository.delete(test_bob_gift['id'])

        query = await db_session.execute(
            text("""
                SELECT *
                FROM gifts
                WHERE id = :gift_id
            """),
            {'gift_id': test_bob_gift['id']},
        )

        assert query.mappings().one_or_none() is None

    async def test_repo_delete_gift_not_exists_dont_raise(
        self,
        gift_repository: GiftRepository,
    ) -> None:
        await gift_repository.delete(123456)

    async def test_repo_get_gift_success(
        self,
        gift_repository: GiftRepository,
        test_bob_gift: GiftDict,
    ) -> None:
        result = await gift_repository.get(
            test_bob_gift['id'],
            test_bob_gift['user_id'],
        )

        assert_that(
            result,
            has_properties(
                id=equal_to(test_bob_gift['id']),
                user_id=equal_to(test_bob_gift['user_id']),
                name=equal_to(test_bob_gift['name']),
                url=equal_to(test_bob_gift['url']),
                wish_rate=equal_to(test_bob_gift['wish_rate']),
                price=equal_to(test_bob_gift['price']),
                note=equal_to(test_bob_gift['note']),
                is_reserved=is_(False),
                reserved_by=is_(none()),
            ),
        )

    async def test_repo_get_gift_not_found_raises(
        self,
        gift_repository: GiftRepository,
        test_user_bob: UserDict,
    ) -> None:
        with pytest.raises(NotFoundInDbError, match='Gift with id=123456 not found'):
            await gift_repository.get(123456, test_user_bob['tg_id'])

    async def test_repo_get_gift_reserved_by_current_user(
        self,
        gift_repository: GiftRepository,
        test_bob_gift: GiftDict,
        test_user_john: UserDict,
        db_session: AsyncSession,
    ) -> None:
        await db_session.execute(
            text("""
                 INSERT INTO gift_reservations (gift_id, reserved_by_tg_id)
                 VALUES (:gift_id, :reserved_by_tg_id)
                 """),
            {'gift_id': test_bob_gift['id'], 'reserved_by_tg_id': test_user_john['tg_id']},
        )
        await db_session.flush()

        result = await gift_repository.get(
            test_bob_gift['id'],
            test_user_john['tg_id'],
        )

        assert_that(
            result,
            has_properties(
                is_reserved=is_(True),
                reserved_by=equal_to(test_user_john['tg_id']),
            ),
        )

    async def test_repo_get_gift_reserved_by_other_user(
        self,
        gift_repository: GiftRepository,
        test_bob_gift: GiftDict,
        test_user_john: UserDict,
        db_session: AsyncSession,
    ) -> None:
        await db_session.execute(
            text("""
                 INSERT INTO gift_reservations (gift_id, reserved_by_tg_id)
                 VALUES (:gift_id, :reserved_by_tg_id)
                 """),
            {'gift_id': test_bob_gift['id'], 'reserved_by_tg_id': test_user_john['tg_id']},
        )
        await db_session.flush()

        result = await gift_repository.get(
            test_bob_gift['id'],
            test_bob_gift['user_id'],
        )

        assert_that(
            result,
            has_properties(
                is_reserved=is_(True),
                reserved_by=is_(none()),
            ),
        )
