from dataclasses import dataclass
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
    is_reserved: bool
    reserved_by: int | None

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
            is_reserved=False,
            reserved_by=None,
        )
