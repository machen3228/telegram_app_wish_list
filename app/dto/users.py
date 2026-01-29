from dataclasses import dataclass
from datetime import datetime


@dataclass
class TelegramAuthDTO:
    init_data: str


@dataclass
class FriendRequestDTO:
    sender_tg_id: int
    receiver_tg_id: int
    status: str
    created_at: datetime
    sender_name: str | None = None
    sender_username: str | None = None
