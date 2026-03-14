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

    def test_gift_domain_can_delete_gift_owner(self, gift_data: dict) -> None:
        gift = Gift.create(**gift_data)

        assert gift.can_delete_gift(gift_data['user_id']) is True

    def test_gift_domain_can_delete_gift_not_owner(self, gift_data: dict) -> None:
        gift = Gift.create(**gift_data)

        assert gift.can_delete_gift(666_666) is False

    @pytest.mark.parametrize(
        ('is_reserved', 'reserved_by', 'who_try', 'result'),
        [
            pytest.param(True, 123_456, 123_456, True, id='Owner reserved, owner try'),
            pytest.param(True, 123_456, 666_666, False, id='Owner reserved, alien tries'),
            pytest.param(True, 111_111, 123_456, True, id='Friend reserved, owner tries'),
            pytest.param(True, 111_111, 111_111, True, id='Friend reserved, friend tries'),
            pytest.param(True, 111_111, 666_666, False, id='Friend reserved, alien tries'),
            pytest.param(False, None, 123_456, False, id='Not reserved, owner tries'),
            pytest.param(False, None, 666_666, False, id='Not reserved, alien tries'),
        ],
    )
    def test_gift_domain_can_delete_reservation(
        self, *, gift_data: dict, is_reserved: bool, reserved_by: int | None, who_try: int, result: bool
    ) -> None:
        now = datetime.now(UTC)
        gift = Gift(**{
            **gift_data,
            'id': 1,
            'is_reserved': is_reserved,
            'reserved_by': reserved_by,
            'created_at': now,
            'updated_at': now,
        })  # ty:ignore[invalid-argument-type]

        assert gift.can_delete_reservation(who_try) is result

    @pytest.mark.parametrize(
        ('user_id', 'error_message'),
        [
            pytest.param(-1, 'User ID must be positive, got: -1', id='negative_user_id'),
            pytest.param(0, 'User ID must be positive, got: 0', id='zero_user_id'),
        ],
    )
    def test_gift_domain_create_validates_user_id(self, gift_data: dict, user_id: int, error_message: str) -> None:
        with pytest.raises(ValueError, match=error_message):
            Gift.create(**{**gift_data, 'user_id': user_id})  # ty:ignore[invalid-argument-type]

    @pytest.mark.parametrize(
        ('name', 'error_message'),
        [
            pytest.param('', 'Gift name cannot be empty', id='empty_name'),
            pytest.param('   ', 'Gift name cannot be empty', id='whitespace_only_name'),
            pytest.param('a' * 101, 'Gift name exceeds maximum length of 100 characters', id='name_too_long'),
        ],
    )
    def test_gift_domain_create_validates_name(self, gift_data: dict, name: str, error_message: str) -> None:
        with pytest.raises(ValueError, match=error_message):
            Gift.create(**{**gift_data, 'name': name})  # ty:ignore[invalid-argument-type]

    def test_gift_domain_create_allows_exact_max_length_name(self, gift_data: dict) -> None:
        exact_length_name = 'a' * 100
        gift = Gift.create(**{**gift_data, 'name': exact_length_name})  # ty:ignore[invalid-argument-type]
        assert gift.name == exact_length_name

    @pytest.mark.parametrize(
        ('url', 'error_message'),
        [
            pytest.param(
                'https://' + 'a' * 500,
                'URL exceeds maximum length of 500 characters',
                id='url_too_long',
            ),
            pytest.param(
                'ftp://example.com',
                r'URL must be a valid HTTP/HTTPS URL, got: ftp://example\.com',
                id='invalid_protocol',
            ),
            pytest.param(
                '/gift.jpg',
                r'URL must be a valid HTTP/HTTPS URL, got: /gift\.jpg',
                id='relative_url',
            ),
        ],
    )
    def test_gift_domain_create_validates_url(self, gift_data: dict, url: str, error_message: str) -> None:
        with pytest.raises(ValueError, match=error_message):
            Gift.create(**{**gift_data, 'url': url})  # ty:ignore[invalid-argument-type]

    @pytest.mark.parametrize(
        'url',
        [
            pytest.param('http://example.com/gift', id='http_url'),
            pytest.param('https://example.com/gift', id='https_url'),
            pytest.param(None, id='none_url'),
        ],
    )
    def test_gift_domain_create_allows_valid_url(self, gift_data: dict, url: str | None) -> None:
        gift = Gift.create(**{**gift_data, 'url': url})  # ty:ignore[invalid-argument-type]
        assert gift.url == url

    def test_gift_domain_create_allows_exact_max_length_url(self, gift_data: dict) -> None:
        exact_length_url = 'https://' + 'a' * 488 + '.jpg'
        expected_max_length = 500
        gift = Gift.create(**{**gift_data, 'url': exact_length_url})  # ty:ignore[invalid-argument-type]
        assert len(gift.url) == expected_max_length  # ty:ignore[invalid-argument-type]

    @pytest.mark.parametrize(
        ('wish_rate', 'error_message'),
        [
            pytest.param(0, 'Wish rate must be between 1 and 10, got: 0', id='wish_rate_zero'),
            pytest.param(11, 'Wish rate must be between 1 and 10, got: 11', id='wish_rate_too_high'),
            pytest.param(-5, 'Wish rate must be between 1 and 10, got: -5', id='wish_rate_negative'),
        ],
    )
    def test_gift_domain_create_validates_wish_rate(self, gift_data: dict, wish_rate: int, error_message: str) -> None:
        with pytest.raises(ValueError, match=error_message):
            Gift.create(**{**gift_data, 'wish_rate': wish_rate})  # ty:ignore[invalid-argument-type]

    @pytest.mark.parametrize(
        'wish_rate',
        [
            pytest.param(1, id='wish_rate_minimum'),
            pytest.param(10, id='wish_rate_maximum'),
            pytest.param(None, id='wish_rate_none'),
        ],
    )
    def test_gift_domain_create_allows_valid_wish_rate(self, gift_data: dict, wish_rate: int | None) -> None:
        gift = Gift.create(**{**gift_data, 'wish_rate': wish_rate})  # ty:ignore[invalid-argument-type]
        assert gift.wish_rate == wish_rate

    @pytest.mark.parametrize(
        ('price', 'error_message'),
        [
            pytest.param(-100, 'Price must be non-negative, got: -100', id='negative_price'),
            pytest.param(100_000_000, 'Price exceeds maximum value of 99999999, got: 100000000', id='price_too_high'),
        ],
    )
    def test_gift_domain_create_validates_price(self, gift_data: dict, price: int, error_message: str) -> None:
        with pytest.raises(ValueError, match=error_message):
            Gift.create(**{**gift_data, 'price': price})  # ty:ignore[invalid-argument-type]

    @pytest.mark.parametrize(
        'price',
        [
            pytest.param(0, id='zero_price'),
            pytest.param(99_999_999, id='maximum_price'),
            pytest.param(None, id='none_price'),
        ],
    )
    def test_gift_domain_create_allows_valid_price(self, gift_data: dict, price: int | None) -> None:
        gift = Gift.create(**{**gift_data, 'price': price})  # ty:ignore[invalid-argument-type]
        assert gift.price == price
