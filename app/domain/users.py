from dataclasses import dataclass
from datetime import UTC, date, datetime
from typing import Self


@dataclass(frozen=True)
class Gift:
    id: int
    user_id: int
    name: str
    url: str
    wish_rate: int
    price: int
    note: str
    created_at: datetime
    updated_at: datetime


class User:
    def __init__(
        self,
        *,
        tg_id: int,
        tg_username: str,
        first_name: str,
        last_name: str | None,
        birthday: date | None,
        created_at: datetime,
        updated_at: datetime,
    ) -> None:
        self.tg_id = tg_id
        self.tg_username = tg_username
        self.first_name = first_name
        self.last_name = last_name
        self.birthday = birthday
        self.created_at = created_at
        self.updated_at = updated_at
        self._gifts: list[Gift] = []

    def __repr__(self) -> str:
        return f'<User {self.tg_id}>'

    @classmethod
    def create(
        cls,
        tg_id: int,
        tg_username: str,
        first_name: str,
        last_name: str | None,
        birthday: date | None,
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            tg_id=tg_id,
            tg_username=tg_username,
            first_name=first_name,
            last_name=last_name,
            birthday=birthday,
            created_at=now,
            updated_at=now,
        )

    def add_gift(self, gift: Gift) -> None:
        self._gifts.append(gift)

    def remove_gift(self, gift: Gift) -> None:
        self._gifts.remove(gift)
