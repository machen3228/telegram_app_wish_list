from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Self

from core.security.telegram_auth import TelegramInitData


@dataclass
class User:
    tg_id: int
    tg_username: str | None
    first_name: str | None
    last_name: str | None
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime
    _friends_ids: set[int] = field(default_factory=set, repr=False)

    def __repr__(self) -> str:
        return f'<User {self.tg_id}>'

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return False
        return self.tg_id == other.tg_id

    def __hash__(self) -> int:
        return hash(self.tg_id)

    @classmethod
    def create(
        cls,
        tg_id: int,
        tg_username: str,
        first_name: str,
        last_name: str | None,
        avatar_url: str | None,
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            tg_id=tg_id,
            tg_username=tg_username,
            first_name=first_name,
            last_name=last_name,
            avatar_url=avatar_url,
            created_at=now,
            updated_at=now,
        )

    def add_friends(self, friends: Sequence[int]) -> None:
        self._friends_ids.update(friends)

    def can_add_friend(self, friend: 'User') -> bool:
        return friend.tg_id not in self._friends_ids

    def get_changed_fields(self, init_data: TelegramInitData) -> dict[str, Any]:
        field_mapping = {
            'username': 'tg_username',
            'first_name': 'first_name',
            'last_name': 'last_name',
            'photo_url': 'avatar_url',
        }
        update_fields: dict[str, Any] = {}

        for telegram_key, model_key in field_mapping.items():
            telegram_value = init_data.get(telegram_key, '')
            current_value = getattr(self, model_key)

            if model_key in ('last_name', 'avatar_url'):
                telegram_value = telegram_value or None
                current_value = current_value or None

            if current_value != telegram_value:
                update_fields[model_key] = telegram_value

        return update_fields
