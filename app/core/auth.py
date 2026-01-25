import hashlib
import hmac
from urllib.parse import parse_qsl

from core.config import settings


def validate_telegram_init_data(init_data: str) -> dict:
    bot_token = settings.bot_token
    try:
        parsed_data = dict(parse_qsl(init_data))
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            msg = 'Hash not found in init_data'
            raise ValueError(msg) from None  # noqa: TRY301
        data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(parsed_data.items()))
        secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if calculated_hash != received_hash:
            msg = 'Invalid hash - data may be tampered'
            raise ValueError(msg)  # noqa: TRY301
    except Exception as e:  # noqa: BLE001
        raise ValueError(f'Init data validation failed: {e}') from None
    return parsed_data
