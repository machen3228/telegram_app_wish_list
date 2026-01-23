import hashlib
import hmac
from typing import Any

from litestar.exceptions import HTTPException

from core.config import settings


def verify_telegram_auth(data: dict[str, Any]) -> dict[str, Any]:
    hash_to_check = str(data.pop('hash'))

    check_string = '\n'.join(f'{k}={v}' for k, v in sorted(data.items()))
    secret_key = hashlib.sha256(settings.bot_token.encode()).digest()
    hmac_hash = hmac.new(secret_key, check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(hmac_hash, hash_to_check):
        raise HTTPException(status_code=403, detail='Invalid Telegram auth data')

    return data
