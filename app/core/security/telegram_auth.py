import hashlib
import hmac
import json
import time
from typing import NotRequired
from typing import TypedDict
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


def get_init_data_from_header(request: Request) -> str:
    init_data = request.headers.get('X-Telegram-Init-Data')
    if not init_data:
        raise UnauthorizedError(detail='Missing X-Telegram-Init-Data header')
    return init_data


def parse_init_data(init_data: str) -> dict:
    return dict(parse_qsl(init_data))


def extract_hash(parsed_data: dict) -> str:
    received_hash = parsed_data.pop('hash', '')
    if not received_hash:
        raise UnauthorizedError(detail='Hash not found in init_data')
    return received_hash


def extract_auth_timestamp(parsed_data: dict) -> int:
    auth_date = parsed_data.get('auth_date', '')
    if not auth_date:
        raise UnauthorizedError(detail='auth_date not found in init_data')
    try:
        return int(auth_date)
    except ValueError as e:
        raise UnauthorizedError(detail='Invalid auth_date format') from e


def check_data_freshness(auth_timestamp: int, max_age: int = settings.app.max_tg_token_age) -> None:
    age = int(time.time()) - auth_timestamp
    if age > max_age:
        raise UnauthorizedError(detail=f'Init data expired (age: {age}s, max: {max_age}s)')


def build_data_check_string(parsed_data: dict) -> str:
    return '\n'.join(f'{k}={v}' for k, v in sorted(parsed_data.items()))


def compute_hmac_signature(data_check_string: str, bot_token: str = settings.bot.token.get_secret_value()) -> str:
    secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
    return hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()


def verify_signature(calculated_hash: str, received_hash: str) -> None:
    if calculated_hash != received_hash:
        raise UnauthorizedError(detail='Invalid hash - data may be tampered')


def parse_user_json(validated_data: dict) -> dict:
    user_json = validated_data.get('user')
    if not user_json:
        raise UnauthorizedError(detail='User data not found in init_data')
    try:
        return json.loads(user_json)
    except json.JSONDecodeError as e:
        raise UnauthorizedError(detail=f'Invalid user JSON: {e}') from e


def validate_user_fields(user_data: dict) -> None:
    if 'id' not in user_data or 'first_name' not in user_data:
        raise UnauthorizedError(detail='Required user fields missing')


def build_telegram_init_data(user_data: dict) -> TelegramInitData:
    result: TelegramInitData = {
        'id': user_data['id'],
        'first_name': user_data['first_name'],
    }
    if username := user_data.get('username'):
        result['username'] = username
    if last_name := user_data.get('last_name'):
        result['last_name'] = last_name
    if photo_url := user_data.get('photo_url'):
        result['photo_url'] = photo_url

    return result


def validate_telegram_init_data(init_data: str) -> dict:
    parsed_data = parse_init_data(init_data)
    received_hash = extract_hash(parsed_data)
    auth_timestamp = extract_auth_timestamp(parsed_data)
    check_data_freshness(auth_timestamp)

    data_check_string = build_data_check_string(parsed_data)
    calculated_hash = compute_hmac_signature(data_check_string)
    verify_signature(calculated_hash, received_hash)

    return parsed_data


def get_telegram_init_data(request: Request) -> TelegramInitData:
    init_data = get_init_data_from_header(request)
    validated_data = validate_telegram_init_data(init_data)

    user_data = parse_user_json(validated_data)
    validate_user_fields(user_data)

    return build_telegram_init_data(user_data)
