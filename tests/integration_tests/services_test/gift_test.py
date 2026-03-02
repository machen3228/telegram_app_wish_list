from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_properties
from hamcrest import not_none
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions.http import ForbiddenError
from exceptions.http import NotFoundError
from services import GiftService
from tests.integration_tests.conftest import GiftDict
from tests.integration_tests.conftest import UserDict


@pytest.mark.integration
@pytest.mark.asyncio
class TestGiftService:
    async def test_service_add_gift_success(
        self,
        db_session: AsyncSession,
        gift_service: GiftService,
        test_user_bob: UserDict,
        gift_data: dict,
    ) -> None:
        gift_id = await gift_service.add(**gift_data, current_user_id=test_user_bob['tg_id'])

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

    async def test_service_add_gift_user_not_found(
        self,
        gift_service: GiftService,
        gift_data: dict,
    ) -> None:
        with pytest.raises(NotFoundError, match='User with id=123456 not found'):
            await gift_service.add(**gift_data, current_user_id=123456)

    async def test_service_delete_gift_success(
        self,
        db_session: AsyncSession,
        gift_service: GiftService,
        test_bob_gift: GiftDict,
    ) -> None:
        await gift_service.delete(test_bob_gift['id'], test_bob_gift['user_id'])

        query = await db_session.execute(
            text("""
                SELECT *
                FROM gifts
                WHERE id = :gift_id
            """),
            {'gift_id': test_bob_gift['id']},
        )

        assert query.mappings().one_or_none() is None

    async def test_service_delete_gift_not_exists_raise(
        self,
        gift_service: GiftService,
        test_user_bob: UserDict,
    ) -> None:
        with pytest.raises(NotFoundError, match='Gift with id=123456 not found'):
            await gift_service.delete(123456, test_user_bob['tg_id'])

    async def test_service_delete_gift_not_owner(
        self,
        gift_service: GiftService,
        test_bob_gift: GiftDict,
    ) -> None:
        with pytest.raises(ForbiddenError):
            await gift_service.delete(test_bob_gift['id'], 666666)

    @pytest.mark.usefixtures('test_user_with_friend')
    async def test_service_add_reservation_success(
        self,
        db_session: AsyncSession,
        gift_service: GiftService,
        test_bob_gift: GiftDict,
        test_user_john: UserDict,
    ) -> None:
        await gift_service.add_reservation(
            gift_id=test_bob_gift['id'],
            current_user_id=test_user_john['tg_id'],
        )
        query = await db_session.execute(
            text("""
                SELECT *
                FROM gift_reservations
                WHERE gift_id = :gift_id
            """),
            {'gift_id': test_bob_gift['id']},
        )

        reservation = query.mappings().first()
        assert_that(
            reservation,
            has_properties(
                gift_id=equal_to(test_bob_gift['id']),
                reserved_by_tg_id=equal_to(test_user_john['tg_id']),
                created_at=not_none(),
            ),
        )

    @pytest.mark.usefixtures('test_user_with_friend')
    async def test_service_add_reservation_gift_not_found(
        self,
        gift_service: GiftService,
        test_user_john: UserDict,
    ) -> None:
        with pytest.raises(NotFoundError, match='Gift with id=999999 not found'):
            await gift_service.add_reservation(
                gift_id=999999,
                current_user_id=test_user_john['tg_id'],
            )

    async def test_service_add_reservation_not_friend_or_owner(
        self,
        gift_service: GiftService,
        test_bob_gift: GiftDict,
        test_user_john: UserDict,
    ) -> None:
        with pytest.raises(ForbiddenError, match='Not a friend or owner'):
            await gift_service.add_reservation(
                gift_id=test_bob_gift['id'],
                current_user_id=test_user_john['tg_id'],
            )

    async def test_service_add_reservation_duplicate_raises(
        self,
        gift_service: GiftService,
        test_bob_gift: GiftDict,
        test_user_bob: UserDict,
    ) -> None:
        await gift_service.add_reservation(
            gift_id=test_bob_gift['id'],
            current_user_id=test_user_bob['tg_id'],
        )

        with pytest.raises(NotFoundError, match=f'Gift with id={test_bob_gift["id"]} already reserved'):
            await gift_service.add_reservation(
                gift_id=test_bob_gift['id'],
                current_user_id=test_user_bob['tg_id'],
            )
