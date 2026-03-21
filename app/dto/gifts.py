from dataclasses import dataclass

from domain.gifts import Gift


@dataclass
class GiftCreateDTO:
    name: str
    url: str | None
    wish_rate: int | None
    price: int | None
    note: str | None


@dataclass(frozen=True)
class GiftOwnerDTO:
    first_name: str | None
    last_name: str | None
    avatar_url: str | None


@dataclass(frozen=True)
class GiftWithOwnerDTO(Gift):
    owner: GiftOwnerDTO
