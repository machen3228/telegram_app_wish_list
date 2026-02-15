from litestar import Request

from core.security.telegram_auth import TelegramInitData, get_telegram_init_data


async def provide_telegram_init_data(request: Request) -> TelegramInitData:
    return get_telegram_init_data(request)
