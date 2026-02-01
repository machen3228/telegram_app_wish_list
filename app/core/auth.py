import hashlib
import hmac
from urllib.parse import parse_qsl


def validate_telegram_init_data(init_data: str, bot_token: str) -> dict:
    try:
        parsed_data = dict(parse_qsl(init_data))
        received_hash = parsed_data.pop('hash', None)
        if not received_hash:
            raise ValueError('Hash not found in init_data')  # noqa: TRY301
        data_check_string = '\n'.join(f'{k}={v}' for k, v in sorted(parsed_data.items()))
        secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
        if calculated_hash != received_hash:
            raise ValueError('Invalid hash - data may be tampered')  # noqa: TRY301
        parsed_data.pop('signature', None)
        return parsed_data  # noqa: TRY300
    except Exception as e:
        raise ValueError(f'Init_data validation failed: {e}') from e
