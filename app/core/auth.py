import hashlib
import hmac
from urllib.parse import parse_qsl

from core.config import settings


def validate_telegram_init_data(init_data: str) -> dict:
    bot_token = settings.bot.token
    try:
        parsed_data = dict(parse_qsl(init_data))
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            raise ValueError('Hash not found in init_data') from None  # noqa: TRY301
        data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(parsed_data.items()))
        secret_key = hmac.new(b'WebAppData', bot_token.get_secret_value().encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if calculated_hash != received_hash:
            raise ValueError('Invalid hash - data may be tampered')  # noqa: TRY301
    except Exception as e:  # noqa: BLE001
        raise ValueError(f'Init data validation failed: {e}') from None
    return parsed_data
