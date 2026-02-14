import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock

import jwt
import pytest
from hamcrest import (
    all_of,
    assert_that,
    equal_to,
    greater_than,
    greater_than_or_equal_to,
    has_entries,
    has_key,
    has_length,
    has_properties,
    instance_of,
    less_than_or_equal_to,
    only_contains,
)
from litestar import Request

from core.config import settings
from core.security.jwt_auth import AccessJWTAuth, BaseJWTAuth, TokenOut
from exceptions.http import UnauthorizedError


@pytest.mark.unit
class TestBaseJWTAuth:
    def test_auth_jwt_create_token(self) -> None:
        subject = 123456
        token_out = BaseJWTAuth.create_token(subject)

        assert_that(
            token_out,
            all_of(
                instance_of(TokenOut),
                has_properties(
                    access_token=all_of(
                        instance_of(str),
                        has_length(greater_than(0)),
                    ),
                    token_type=equal_to("Bearer"),
                ),
            ),
        )

    def test_auth_jwt_create_token_payload_contains_correct_data(self) -> None:
        subject = 123456
        token_out = BaseJWTAuth.create_token(subject)

        payload = jwt.decode(
            token_out.access_token,
            settings.jwt.secret_key.get_secret_value(),
            settings.jwt.algorithm,
        )

        assert_that(
            payload,
            all_of(
                has_entries({
                    "sub": str(subject),
                    "type": "access",
                }),
                has_key("exp"),
            ),
        )

    def test_auth_jwt_create_token_expiration_time(self) -> None:
        subject = 123456
        before_creation = datetime.now(UTC).replace(microsecond=0)
        token_out = BaseJWTAuth.create_token(subject)
        after_creation = datetime.now(UTC).replace(microsecond=0)

        payload = jwt.decode(
            token_out.access_token,
            settings.jwt.secret_key.get_secret_value(),
            settings.jwt.algorithm,
        )

        exp_time = datetime.fromtimestamp(payload['exp'], UTC)
        expected_min = before_creation + settings.jwt.access_token_expires
        expected_max = after_creation + settings.jwt.access_token_expires

        assert_that(
            exp_time,
            all_of(
                greater_than_or_equal_to(expected_min),
                less_than_or_equal_to(expected_max),
            ),
        )

    def test_auth_jwt_verify_token(self) -> None:
        subject = 123456
        token_out = BaseJWTAuth.create_token(subject)

        payload = BaseJWTAuth.verify_token(token_out.access_token)

        assert_that(
            payload,
            all_of(
                instance_of(dict),
                has_entries({
                    "exp": instance_of(int),
                    "sub": str(subject),
                    "type": "access",
                }),
            ),
        )

    def test_auth_jwt_verify_token_invalid_signature(self) -> None:
        payload = {
            'sub': '123456',
            'exp': datetime.now(UTC) + timedelta(hours=1),
            'type': 'access',
        }
        invalid_token = jwt.encode(payload, 'wrong-secret-key', settings.jwt.algorithm)
        with pytest.raises(UnauthorizedError) as exc_info:
            BaseJWTAuth.verify_token(invalid_token)

        assert 'Signature verification failed' in str(exc_info.value.detail)

    def test_auth_jwt_verify_token_expired_token(self) -> None:
        payload = {
            'sub': '123456',
            'exp': datetime.now(UTC) - timedelta(hours=1),
            'type': 'access',
        }
        expired_token = jwt.encode(
            payload,
            settings.jwt.secret_key.get_secret_value(),
            algorithm=settings.jwt.algorithm,
        )
        with pytest.raises(UnauthorizedError) as exc_info:
            BaseJWTAuth.verify_token(expired_token)

        assert 'Signature has expired' in str(exc_info.value.detail)

    def test_auth_jwt_verify_invalid_token_type(self) -> None:
        payload = {
            'sub': '123456',
            'exp': datetime.now(UTC) + timedelta(hours=1),
            'type': 'refresh',
        }
        token = jwt.encode(
            payload,
            settings.jwt.secret_key.get_secret_value(),
            algorithm=settings.jwt.algorithm,
        )
        with pytest.raises(UnauthorizedError) as exc_info:
            BaseJWTAuth.verify_token(token)

        assert exc_info.value.detail == "Invalid token type: expected 'access'"

    def test_auth_jwt_verify_malformed_token(self) -> None:
        malformed_token = 'this.is.not.a.valid.jwt.token'  # noqa: S105
        with pytest.raises(UnauthorizedError):
            BaseJWTAuth.verify_token(malformed_token)

    def test_auth_jwt_verify_missing_type_field(self) -> None:
        payload = {
            'sub': '123456',
            'exp': datetime.now(UTC) + timedelta(hours=1),
            # 'type' is missing
        }
        token = jwt.encode(
            payload,
            settings.jwt.secret_key.get_secret_value(),
            algorithm=settings.jwt.algorithm,
        )
        with pytest.raises(UnauthorizedError, match="Invalid token type: expected 'access'"):
            BaseJWTAuth.verify_token(token)


@pytest.mark.unit
@pytest.mark.asyncio
class TestAccessJWTAuth:
    @pytest.fixture
    def auth(self) -> AccessJWTAuth:
        return AccessJWTAuth()

    @pytest.fixture
    def valid_token(self) -> str:
        return BaseJWTAuth.create_token(123456).access_token

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        request = MagicMock(spec=Request)
        request.headers = {}
        return request

    async def test_auth_jwt_call_with_valid_bearer_token(
        self,
        auth: AccessJWTAuth,
        mock_request: MagicMock,
        valid_token: str,
    ) -> None:
        mock_request.headers = {'Authorization': f'Bearer {valid_token}'}
        user_id = await auth(mock_request)

        assert_that(
            user_id,
            all_of(
                instance_of(int),
                equal_to(123456),
            ),
        )

    async def test_auth_jwt_call_without_authorization_header(
        self,
        auth: AccessJWTAuth,
        mock_request: MagicMock,
    ) -> None:
        mock_request.headers = {}
        with pytest.raises(UnauthorizedError, match='Unauthorized'):
            await auth(mock_request)

    async def test_auth_jwt_call_with_empty_authorization_header(
        self,
        auth: AccessJWTAuth,
        mock_request: MagicMock,
    ) -> None:
        mock_request.headers = {'Authorization': ''}
        with pytest.raises(UnauthorizedError, match='Invalid authorization scheme'):
            await auth(mock_request)

    async def test_auth_jwt_call_with_invalid_scheme(
        self,
        auth: AccessJWTAuth,
        mock_request: MagicMock,
        valid_token: str,
    ) -> None:
        mock_request.headers = {'Authorization': f'Basic {valid_token}'}
        with pytest.raises(UnauthorizedError, match='Invalid authorization scheme'):
            await auth(mock_request)

    async def test_auth_jwt_call_with_empty_token(
        self,
        auth: AccessJWTAuth,
        mock_request: MagicMock,
    ) -> None:
        mock_request.headers = {'Authorization': 'Bearer'}
        with pytest.raises(UnauthorizedError, match='Invalid authorization scheme'):
            await auth(mock_request)

    async def test_auth_jwt_call_with_lowercase_bearer(
        self,
        auth: AccessJWTAuth,
        mock_request: MagicMock,
        valid_token: str,
    ) -> None:
        mock_request.headers = {'Authorization': f'bearer {valid_token}'}
        user_id = await auth(mock_request)

        assert user_id == 123456  # noqa: PLR2004

    async def test_auth_jwt_call_with_uppercase_bearer(
        self,
        auth: AccessJWTAuth,
        mock_request: MagicMock,
        valid_token: str,
    ) -> None:
        mock_request.headers = {'Authorization': f'BEARER {valid_token}'}
        user_id = await auth(mock_request)

        assert user_id == 123456  # noqa: PLR2004

    async def test_auth_jwt_call_with_invalid_token(
        self,
        auth: AccessJWTAuth,
        mock_request: MagicMock,
    ) -> None:
        mock_request.headers = {'Authorization': 'Bearer invalid.token.here'}
        with pytest.raises(UnauthorizedError):
            await auth(mock_request)

    async def test_auth_jwt_call_multiple_concurrent_auth_calls(
        self,
        auth: AccessJWTAuth,
        mock_request: MagicMock,
        valid_token: str,
    ) -> None:
        async def authenticate() -> int:
            mock_request.headers = {'Authorization': f'Bearer {valid_token}'}
            return await auth(mock_request)

        results = await asyncio.gather(*[authenticate() for _ in range(10)])

        assert_that(
            results,
            all_of(
                has_length(10),
                only_contains(123456),
            ),
        )
