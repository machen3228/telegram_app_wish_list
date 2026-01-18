from dataclasses import dataclass


@dataclass
class GiftCreateDTO:
    user_id: int
    name: str
    url: str | None
    wish_rate: int | None
    price: int | None
    note: str | None
