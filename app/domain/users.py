from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Self


@dataclass(frozen=True)
class Gift:
    id: int | None
    user_id: int
    name: str
    url: str | None
    wish_rate: int | None
    price: int | None
    note: str | None
    created_at: datetime
    updated_at: datetime

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Gift):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def create(
        cls,
        user_id: int,
        name: str,
        url: str | None,
        wish_rate: int | None,
        price: int | None,
        note: str | None,
    ) -> Self:
        now = datetime.now(UTC)
        return cls(
            id=None,
            user_id=user_id,
            name=name,
            url=url,
            wish_rate=wish_rate,
            price=price,
            note=note,
            created_at=now,
            updated_at=now,
        )


@dataclass
class User:
    tg_id: int
    tg_username: str
    first_name: str
    last_name: str | None
    avatar_url: str | None
    created_at: datetime
    updated_at: datetime
    gifts: set['Gift'] = field(default_factory=set, repr=False)
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

    def add_gifts(self, gifts: Sequence['Gift']) -> None:
        self.gifts.update(gift for gift in gifts)

    def add_friends(self, friends: Sequence[int]) -> None:
        self._friends_ids.update(friends)

    def can_add_friend(self, friend: 'User') -> bool:
        return friend.tg_id not in self._friends_ids

    def can_delete_friend(self, friend: 'User') -> bool:
        return friend.tg_id in self._friends_ids
