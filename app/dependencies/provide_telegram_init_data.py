from litestar import Request

from core.security import TelegramInitData
from core.security import get_telegram_init_data


def provide_telegram_init_data(request: Request) -> TelegramInitData:
    return get_telegram_init_data(request)
