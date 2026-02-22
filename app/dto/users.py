from dataclasses import dataclass
from datetime import datetime


@dataclass
class FriendRequestDTO:
    sender_tg_id: int
    receiver_tg_id: int
    status: str
    created_at: datetime
    sender_name: str | None = None
    sender_username: str | None = None


@dataclass
class UserRelationsDTO:
    friends_ids: set[int]
    incoming_requests: dict[int, str]
    outgoing_requests: dict[int, str]
