from datetime import UTC
from datetime import datetime
from typing import Any
from typing import TypedDict

import jwt
from litestar import Request
from pydantic import BaseModel

from core import settings
from exceptions.http import UnauthorizedError


class TokenOut(BaseModel):
    token_type: str = 'Bearer'  # noqa: S105
    access_token: str


class Payload(TypedDict):
    sub: str
    exp: datetime
    type: str


class BaseJWTAuth:
    @staticmethod
    def verify_token(token: str) -> Payload:
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                settings.jwt.secret_key.get_secret_value(),
                algorithms=settings.jwt.algorithm,
            )
            if payload.get('type') != 'access':
                raise UnauthorizedError(detail="Invalid token type: expected 'access'")
        except jwt.exceptions.InvalidTokenError as exc:
            raise UnauthorizedError(detail=str(exc)) from exc
        else:
            return Payload(sub=payload['sub'], exp=payload['exp'], type=payload['type'])

    @classmethod
    def create_token(cls, subject: int) -> TokenOut:
        expire = datetime.now(UTC) + settings.jwt.access_token_expires
        payload = {'sub': str(subject), 'exp': expire, 'type': 'access'}

        access_token = jwt.encode(
            payload,
            settings.jwt.secret_key.get_secret_value(),
            settings.jwt.algorithm,
        )

        return TokenOut(access_token=access_token)


class AccessJWTAuth(BaseJWTAuth):
    async def __call__(self, request: Request) -> int:
        authorization = request.headers.get('Authorization')

        if authorization is None:
            raise UnauthorizedError(detail='Unauthorized')

        if not authorization.strip():
            raise UnauthorizedError(detail='Invalid authorization scheme')

        scheme, _, token = authorization.partition(' ')

        if scheme.lower() != 'bearer' or not token:
            raise UnauthorizedError(detail='Invalid authorization scheme')

        payload = self.verify_token(token)
        return int(payload['sub'])
