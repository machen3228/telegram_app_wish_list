from dataclasses import dataclass
from datetime import UTC
from datetime import datetime
from typing import Final
from typing import Self

MAX_NAME_LENGTH: Final[int] = 100
MAX_URL_LENGTH: Final[int] = 500
MIN_WISH_RATE: Final[int] = 1
MAX_WISH_RATE: Final[int] = 10
MAX_PRICE: Final[int] = 99_999_999


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
        cls._validate_user_id(user_id)
        cls._validate_name(name)
        cls._validate_url(url)
        cls._validate_wish_rate(wish_rate)
        cls._validate_price(price)

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

    @staticmethod
    def _validate_user_id(user_id: int) -> None:
        if user_id <= 0:
            raise ValueError(f'User ID must be positive, got: {user_id}')

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name or not name.strip():
            raise ValueError('Gift name cannot be empty')
        if len(name) > MAX_NAME_LENGTH:
            raise ValueError(
                f'Gift name exceeds maximum length of {MAX_NAME_LENGTH} characters (got {len(name)} characters)'
            )

    @staticmethod
    def _validate_url(url: str | None) -> None:
        if url and len(url) > MAX_URL_LENGTH:
            raise ValueError(f'URL exceeds maximum length of {MAX_URL_LENGTH} characters (got {len(url)} characters)')
        if url and not url.startswith(('http://', 'https://')):
            raise ValueError(f'URL must be a valid HTTP/HTTPS URL, got: {url}')

    @staticmethod
    def _validate_wish_rate(wish_rate: int | None) -> None:
        if wish_rate is not None and (wish_rate < MIN_WISH_RATE or wish_rate > MAX_WISH_RATE):
            raise ValueError(f'Wish rate must be between {MIN_WISH_RATE} and {MAX_WISH_RATE}, got: {wish_rate}')

    @staticmethod
    def _validate_price(price: int | None) -> None:
        if price is not None and price < 0:
            raise ValueError(f'Price must be non-negative, got: {price}')
        if price is not None and price > MAX_PRICE:
            raise ValueError(f'Price exceeds maximum value of {MAX_PRICE}, got: {price}')

    def can_delete_gift(self, user_id: int) -> bool:
        return self.user_id == user_id

    def can_delete_reservation(self, user_id: int) -> bool:
        return user_id in (self.user_id, self.reserved_by) and self.is_reserved
