from dataclasses import dataclass
from datetime import date


@dataclass
class UserCreateDTO:
    tg_id: int
    tg_username: str
    first_name: str
    last_name: str | None
    birthday: date | None
