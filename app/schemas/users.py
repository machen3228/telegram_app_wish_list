from datetime import date

from pydantic import BaseModel


class UserCreateDTO(BaseModel):
    tg_id: int
    tg_username: str
    first_name: str
    last_name: str | None = None
    birthday: date | None = None
