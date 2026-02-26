from dataclasses import FrozenInstanceError
from datetime import UTC
from datetime import datetime

import pytest

from domain import Gift


@pytest.mark.unit
class TestUserDomain:
    def test_gift_domain_create_sets_id_to_none(self, gift_data: dict) -> None:
        gift = Gift.create(**gift_data)
        assert gift.id is None

    def test_gift_domain_create_sets_is_reserved_to_false(self, gift_data: dict) -> None:
        gift = Gift.create(**gift_data)
        assert gift.is_reserved is False

    def test_gift_domain_create_sets_reserved_by_to_none(self, gift_data: dict) -> None:
        gift = Gift.create(**gift_data)
        assert gift.reserved_by is None

    def test_gift_domain_create_sets_created_at_and_updated_at_equal(self, gift_data: dict) -> None:
        gift = Gift.create(**gift_data)
        assert gift.created_at == gift.updated_at

    def test_gift_domain_create_timestamps_are_recent(self, gift_data: dict) -> None:
        before = datetime.now(UTC)
        gift = Gift.create(**gift_data)
        after = datetime.now(UTC)
        assert before <= gift.created_at <= after

    def test_gift_domain_create_timestamps_are_utc(self, gift_data: dict) -> None:
        gift = Gift.create(**gift_data)
        assert gift.created_at.tzinfo == UTC

    @pytest.mark.parametrize('field', ['user_id', 'name', 'url', 'wish_rate', 'price', 'note'])
    def test_gift_domain_create_stores_correct_fields(self, gift_data: dict, field: str) -> None:
        gift = Gift.create(**gift_data)
        assert getattr(gift, field) == gift_data[field]

    @pytest.mark.parametrize(
        ('field', 'value'),
        [
            ('url', None),
            ('wish_rate', None),
            ('price', None),
            ('note', None),
        ],
    )
    def test_gift_domain_create_optional_fields_accept_none(self, gift_data: dict, field: str, value: None) -> None:
        gift = Gift.create(**{**gift_data, field: value})  # ty:ignore[invalid-argument-type]
        assert getattr(gift, field) is None

    def test_gift_domain_equality_by_id(self, gift_data: dict) -> None:
        gift1 = Gift(**{
            **gift_data,
            'id': 1,
            'is_reserved': False,
            'reserved_by': None,
            'created_at': datetime.now(UTC),
            'updated_at': datetime.now(UTC),
        })  # ty:ignore[invalid-argument-type]
        gift2 = Gift(**{
            **gift_data,
            'id': 1,
            'name': 'Other',
            'is_reserved': False,
            'reserved_by': None,
            'created_at': datetime.now(UTC),
            'updated_at': datetime.now(UTC),
        })  # ty:ignore[invalid-argument-type]
        assert gift1 == gift2

    def test_gift_domain_inequality_different_ids(self, gift_data: dict) -> None:
        now = datetime.now(UTC)
        gift1 = Gift(**{
            **gift_data,
            'id': 1,
            'is_reserved': False,
            'reserved_by': None,
            'created_at': now,
            'updated_at': now,
        })  # ty:ignore[invalid-argument-type]
        gift2 = Gift(**{
            **gift_data,
            'id': 2,
            'is_reserved': False,
            'reserved_by': None,
            'created_at': now,
            'updated_at': now,
        })  # ty:ignore[invalid-argument-type]
        assert gift1 != gift2

    def test_gift_domain_equality_with_non_gift_object(self, gift_data: dict) -> None:
        now = datetime.now(UTC)
        gift = Gift(**{
            **gift_data,
            'id': 1,
            'is_reserved': False,
            'reserved_by': None,
            'created_at': now,
            'updated_at': now,
        })  # ty:ignore[invalid-argument-type]
        assert gift != 'not a gift'

    def test_gift_domain_hash_equal_for_same_id(self, gift_data: dict) -> None:
        now = datetime.now(UTC)
        gift1 = Gift(**{
            **gift_data,
            'id': 1,
            'is_reserved': False,
            'reserved_by': None,
            'created_at': now,
            'updated_at': now,
        })  # ty:ignore[invalid-argument-type]
        gift2 = Gift(**{
            **gift_data,
            'id': 1,
            'name': 'Other',
            'is_reserved': False,
            'reserved_by': None,
            'created_at': now,
            'updated_at': now,
        })  # ty:ignore[invalid-argument-type]
        assert hash(gift1) == hash(gift2)

    def test_gift_domain_usable_in_set(self, gift_data: dict) -> None:
        now = datetime.now(UTC)
        gift1 = Gift(**{
            **gift_data,
            'id': 1,
            'is_reserved': False,
            'reserved_by': None,
            'created_at': now,
            'updated_at': now,
        })  # ty:ignore[invalid-argument-type]
        gift2 = Gift(**{
            **gift_data,
            'id': 1,
            'is_reserved': False,
            'reserved_by': None,
            'created_at': now,
            'updated_at': now,
        })  # ty:ignore[invalid-argument-type]
        gift3 = Gift(**{
            **gift_data,
            'id': 2,
            'is_reserved': False,
            'reserved_by': None,
            'created_at': now,
            'updated_at': now,
        })  # ty:ignore[invalid-argument-type]
        assert len({gift1, gift2, gift3}) == 2  # noqa: PLR2004

    def test_gift_domain_is_frozen(self, gift_data: dict) -> None:
        gift = Gift.create(**gift_data)
        with pytest.raises(FrozenInstanceError):
            gift.name = 'New Name'  # ty:ignore[invalid-assignment]
