import json

from litestar import Request
from litestar.exceptions import HTTPException

from core.auth import validate_telegram_init_data
from core.config import settings


async def get_current_user_id(request: Request) -> int:
    init_data = request.headers.get('X-Telegram-Init-Data')
    if not init_data:
        raise HTTPException(status_code=401, detail='Missing X-Telegram-Init-Data header')
    try:
        validated_data = validate_telegram_init_data(init_data, settings.bot.token.get_secret_value())
        user_json = validated_data.get('user')
        if not user_json:
            raise ValueError('User data not found in init_data')  # noqa: TRY301
        user_data = json.loads(user_json)
        user_id = user_data.get('id')
        if not user_id:
            raise ValueError('User ID not found')  # noqa: TRY301
        return user_id  # noqa: TRY300
    except ValueError as e:
        raise HTTPException(status_code=401, detail=f'Invalid init_data: {e!s}') from None
