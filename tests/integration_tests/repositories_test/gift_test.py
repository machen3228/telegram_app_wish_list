from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_properties
from hamcrest import not_none
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from domain import Gift
from exceptions.database import NotFoundInDbError
from repositories import GiftRepository
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

        async with db_session as session:
            query = await session.execute(
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
