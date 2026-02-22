from collections.abc import Callable
import hashlib
import hmac
import time
from unittest.mock import MagicMock
from urllib.parse import urlencode

from hamcrest import all_of
from hamcrest import assert_that
from hamcrest import equal_to
from hamcrest import has_entries
from hamcrest import has_length
from hamcrest import matches_regexp
import pytest

from core.config import settings
from core.security import telegram_auth
from exceptions.http import UnauthorizedError


@pytest.mark.unit
class TestTelegramAuth:
    @pytest.mark.parametrize(
        ('init_data', 'expected'),
        [
            (
                'auth_date=1700000000&user=%7B%22id%22%3A123%7D&hash=abc',
                {'auth_date': '1700000000', 'user': '{"id":123}', 'hash': 'abc'},
            ),
            (
                'auth_date=1700000000&hash=abc',
                {'auth_date': '1700000000', 'hash': 'abc'},
            ),
            (
                '',
                {},
            ),
        ],
        ids=['full_data', 'minimal_data', 'empty_string'],
    )
    def test_tg_auth_parse_init_data(self, init_data: str, expected: dict) -> None:
        result = telegram_auth.parse_init_data(init_data)

        assert result == expected

    @pytest.mark.parametrize(
        ('parsed_data', 'expected_hash'),
        [
            (
                {'auth_date': '1700000000', 'user': '{"id":123}', 'hash': 'abc123'},
                'abc123',
            ),
            (
                {'hash': 'onlyhash'},
                'onlyhash',
            ),
        ],
        ids=['full_data', 'only_hash'],
    )
    def test_tg_auth_extract_hash_success(
        self,
        parsed_data: dict,
        expected_hash: str,
    ) -> None:
        result = telegram_auth.extract_hash(parsed_data)

        assert result == expected_hash

    def test_tg_auth_extract_hash_remove_hash_from_dict(self) -> None:
        initial_data = {'auth_date': '1700000000', 'user': '{"id":123}', 'hash': 'abc123'}
        telegram_auth.extract_hash(initial_data)

        assert initial_data == {'auth_date': '1700000000', 'user': '{"id":123}'}

    def test_tg_auth_extract_hash_missing(self) -> None:
        with pytest.raises(UnauthorizedError, match='Hash not found'):
            telegram_auth.extract_hash({'auth_date': '1700000000'})

    @pytest.mark.parametrize(
        ('parsed_data', 'expected_timestamp'),
        [
            ({'auth_date': '1700000000'}, 1700000000),
            ({'auth_date': '0'}, 0),
        ],
        ids=['valid_timestamp', 'zero_timestamp'],
    )
    def test_tg_auth_extract_auth_timestamp_success(
        self,
        parsed_data: dict,
        expected_timestamp: int,
    ) -> None:
        result = telegram_auth.extract_auth_timestamp(parsed_data)

        assert result == expected_timestamp

    @pytest.mark.parametrize(
        ('parsed_data', 'expected_error'),
        [
            ({}, 'auth_date not found'),
            ({'auth_date': 'not_a_number'}, 'Invalid auth_date format'),
        ],
        ids=['missing_auth_date', 'invalid_format'],
    )
    def test_tg_auth_extract_auth_timestamp_failure(
        self,
        parsed_data: dict,
        expected_error: str,
    ) -> None:
        with pytest.raises(UnauthorizedError, match=expected_error):
            telegram_auth.extract_auth_timestamp(parsed_data)

    def test_tg_auth_check_data_freshness_success(self) -> None:

        fresh_timestamp = int(time.time()) - 100
        telegram_auth.check_data_freshness(fresh_timestamp)

    @pytest.mark.parametrize(
        ('age_offset', 'max_age'),
        [
            (86401, 86400),
            (99999, 86400),
        ],
        ids=['just_expired', 'very_old'],
    )
    def test_tg_auth_check_data_freshness_expired(
        self,
        age_offset: int,
        max_age: int,
    ) -> None:
        expired_timestamp = int(time.time()) - age_offset

        with pytest.raises(UnauthorizedError, match='Init data expired'):
            telegram_auth.check_data_freshness(expired_timestamp, max_age)

    @pytest.mark.parametrize(
        ('parsed_data', 'expected'),
        [
            (
                {'auth_date': '1700000000', 'user': '{"id":123}'},
                'auth_date=1700000000\nuser={"id":123}',
            ),
            (
                {'user': '{"id":123}', 'auth_date': '1700000000'},
                'auth_date=1700000000\nuser={"id":123}',
            ),
            (
                {'auth_date': '1700000000'},
                'auth_date=1700000000',
            ),
        ],
        ids=['sorted_order', 'unsorted_input', 'single_field'],
    )
    def test_tg_auth_build_data_check_string(
        self,
        parsed_data: dict,
        expected: str,
    ) -> None:
        result = telegram_auth.build_data_check_string(parsed_data)

        assert result == expected

    def test_tg_auth_compute_hmac_signature_returns_hex_string(
        self,
    ) -> None:
        result = telegram_auth.compute_hmac_signature('auth_date=1700000000')

        assert_that(
            result,
            all_of(
                matches_regexp(r'^[0-9a-f]+$'),
                has_length(64),
            ),
        )

    def test_tg_auth_compute_hmac_signature_deterministic(
        self,
    ) -> None:
        result_1 = telegram_auth.compute_hmac_signature('auth_date=1700000000')
        result_2 = telegram_auth.compute_hmac_signature('auth_date=1700000000')

        assert result_1 == result_2

    def test_tg_auth_compute_hmac_signature_different_inputs(
        self,
    ) -> None:
        result_1 = telegram_auth.compute_hmac_signature('auth_date=1700000000')
        result_2 = telegram_auth.compute_hmac_signature('auth_date=9999999999')

        assert result_1 != result_2

    def test_tg_auth_verify_signature_success(self) -> None:
        telegram_auth.verify_signature('abc123', 'abc123')

    def test_tg_auth_verify_signature_failure(self) -> None:
        with pytest.raises(UnauthorizedError, match='Invalid hash'):
            telegram_auth.verify_signature('abc123', 'wrong_hash')

    @pytest.mark.parametrize(
        ('validated_data', 'expected'),
        [
            (
                {'user': '{"id": 123, "first_name": "Ivan"}'},
                {'id': 123, 'first_name': 'Ivan'},
            ),
            (
                {'user': '{"id": 123, "first_name": "Ivan", "username": "ivan"}'},
                {'id': 123, 'first_name': 'Ivan', 'username': 'ivan'},
            ),
        ],
        ids=['minimal_fields', 'with_username'],
    )
    def test_tg_auth_parse_user_json_success(
        self,
        validated_data: dict,
        expected: dict,
    ) -> None:
        result = telegram_auth.parse_user_json(validated_data)

        assert result == expected

    @pytest.mark.parametrize(
        ('validated_data', 'expected_error'),
        [
            ({}, 'User data not found'),
            ({'user': 'not_a_json'}, 'Invalid user JSON'),
        ],
        ids=['missing_user', 'invalid_json'],
    )
    def test_tg_auth_parse_user_json_failure(
        self,
        validated_data: dict,
        expected_error: str,
    ) -> None:
        with pytest.raises(UnauthorizedError, match=expected_error):
            telegram_auth.parse_user_json(validated_data)

    @pytest.mark.parametrize(
        'user_data',
        [
            {'id': 123, 'first_name': 'Ivan'},
            {'id': 123, 'first_name': 'Ivan', 'username': 'ivan', 'last_name': 'Ivanov'},
        ],
        ids=['minimal_fields', 'full_fields'],
    )
    def test_tg_auth_validate_user_fields_success(
        self,
        user_data: dict,
    ) -> None:
        telegram_auth.validate_user_fields(user_data)

    @pytest.mark.parametrize(
        'user_data',
        [
            {'first_name': 'Ivan'},
            {'id': 123},
            {},
        ],
        ids=['missing_id', 'missing_first_name', 'empty_dict'],
    )
    def test_tg_auth_validate_user_fields_failure(
        self,
        user_data: dict,
    ) -> None:
        with pytest.raises(UnauthorizedError, match='Required user fields missing'):
            telegram_auth.validate_user_fields(user_data)

    @pytest.mark.parametrize(
        ('user_data', 'expected'),
        [
            (
                {'id': 123, 'first_name': 'Ivan'},
                {'id': 123, 'first_name': 'Ivan'},
            ),
            (
                {'id': 123, 'first_name': 'Ivan', 'username': 'ivan'},
                {'id': 123, 'first_name': 'Ivan', 'username': 'ivan'},
            ),
            (
                {'id': 123, 'first_name': 'Ivan', 'last_name': 'Ivanov'},
                {'id': 123, 'first_name': 'Ivan', 'last_name': 'Ivanov'},
            ),
            (
                {
                    'id': 123,
                    'first_name': 'Ivan',
                    'username': 'ivan',
                    'last_name': 'Ivanov',
                    'photo_url': 'https://t.me/photo.jpg',
                },
                {
                    'id': 123,
                    'first_name': 'Ivan',
                    'username': 'ivan',
                    'last_name': 'Ivanov',
                    'photo_url': 'https://t.me/photo.jpg',
                },
            ),
        ],
        ids=['minimal_fields', 'with_username', 'with_last_name', 'full_fields'],
    )
    def test_tg_auth_build_telegram_init_data(
        self,
        user_data: dict,
        expected: dict,
    ) -> None:
        result = telegram_auth.build_telegram_init_data(user_data)

        assert result == expected

    @staticmethod
    def _build_valid_init_data(extra_fields: dict | None = None) -> str:
        data = {
            'auth_date': str(int(time.time())),
            'user': '{"id":123,"first_name":"Ivan"}',
            **(extra_fields or {}),
        }
        data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(data.items()))
        secret_key = hmac.new(b'WebAppData', settings.bot.token.get_secret_value().encode(), hashlib.sha256).digest()
        signature = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        data['hash'] = signature
        return urlencode(data)

    def test_tg_auth_validate_telegram_init_data_success(
        self,
    ) -> None:
        result = telegram_auth.validate_telegram_init_data(self._build_valid_init_data())

        assert_that(result, has_entries({'auth_date': str(int(time.time()))}))

    @pytest.mark.parametrize(
        ('init_data_builder', 'expected_error'),
        [
            (
                lambda: f'auth_date={int(time.time())}&user=%7B%22id%22%3A123%7D&hash=invalidhash',
                'Invalid hash',
            ),
            (
                lambda: f'auth_date={int(time.time())}&user=%7B%22id%22%3A123%7D',
                'Hash not found',
            ),
            (
                lambda: 'user=%7B%22id%22%3A123%7D&hash=abc',
                'auth_date not found',
            ),
        ],
        ids=['invalid_hash', 'missing_hash', 'missing_auth_date'],
    )
    def test_tg_auth_validate_telegram_init_data_failure(
        self,
        init_data_builder: Callable,
        expected_error: str,
    ) -> None:
        with pytest.raises(UnauthorizedError, match=expected_error):
            telegram_auth.validate_telegram_init_data(init_data_builder())

    def test_tg_auth_get_telegram_init_data_success(
        self,
    ) -> None:
        init_data = self._build_valid_init_data()
        request = MagicMock()
        request.headers.get.return_value = init_data

        result = telegram_auth.get_telegram_init_data(request)

        assert_that(result, equal_to({'id': 123, 'first_name': 'Ivan'}))

    def test_tg_auth_get_telegram_init_data_missing_header(self) -> None:
        request = MagicMock()
        request.headers.get.return_value = None

        with pytest.raises(UnauthorizedError, match='Missing X-Telegram-Init-Data header'):
            telegram_auth.get_telegram_init_data(request)
