from litestar import Request

from core.security import TelegramInitData
from core.security import get_telegram_init_data


async def provide_telegram_init_data(request: Request) -> TelegramInitData:  # TODO: make sync
    return get_telegram_init_data(request)
