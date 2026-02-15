import hashlib
import hmac
import json
import time
from typing import NotRequired, TypedDict
from urllib.parse import parse_qsl

from litestar import Request

from core.config import settings
from exceptions.http import UnauthorizedError


class TelegramInitData(TypedDict):
    id: int
    first_name: str
    username: NotRequired[str]
    last_name: NotRequired[str]
    photo_url: NotRequired[str]


def validate_telegram_init_data(init_data: str, bot_token: str, max_age: int = 86400) -> dict:
    parsed_data = dict(parse_qsl(init_data))

    received_hash = parsed_data.pop('hash', None)
    if not received_hash:
        raise UnauthorizedError(detail='Hash not found in init_data')

    auth_date = parsed_data.get('auth_date')
    if not auth_date:
        raise UnauthorizedError(detail='auth_date not found in init_data')

    try:
        auth_timestamp = int(auth_date)
        current_timestamp = int(time.time())
        if current_timestamp - auth_timestamp > max_age:
            raise UnauthorizedError(
                detail=f'Init data expired (age: {current_timestamp - auth_timestamp}s, max: {max_age}s)'
            )
    except ValueError as e:
        raise UnauthorizedError(detail='Invalid auth_date format') from e

    data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(parsed_data.items()))
    secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
    calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    if calculated_hash != received_hash:
        raise UnauthorizedError(detail='Invalid hash - data may be tampered')
    return parsed_data


def get_telegram_init_data(request: Request) -> TelegramInitData:
    init_data = request.headers.get('X-Telegram-Init-Data')
    if not init_data:
        raise UnauthorizedError(detail='Missing X-Telegram-Init-Data header')

    validated_data = validate_telegram_init_data(init_data, settings.bot.token.get_secret_value())

    user_json = validated_data.get('user')
    if not user_json:
        raise UnauthorizedError(detail='User data not found in init_data')

    try:
        user_data = json.loads(user_json)
    except json.JSONDecodeError as e:
        raise UnauthorizedError(detail=f'Invalid user JSON: {e}') from e

    if 'id' not in user_data or 'first_name' not in user_data:
        raise UnauthorizedError(detail='Required user fields missing')

    return TelegramInitData(
        id=user_data['id'],
        first_name=user_data['first_name'],
        username=user_data.get('username'),
        last_name=user_data.get('last_name'),
        photo_url=user_data.get('photo_url'),
    )
