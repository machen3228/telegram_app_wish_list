from dataclasses import dataclass


@dataclass
class GiftCreateDTO:
    name: str
    url: str | None
    wish_rate: int | None
    price: int | None
    note: str | None
