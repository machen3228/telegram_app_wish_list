from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class UserCreateDTO(BaseModel):
    tg_id: int
    tg_username: str
    first_name: str
    last_name: str | None = None
    birthday: date | None = None


class UserReadDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    tg_id: int
    tg_username: str
    first_name: str
    last_name: str | None = None
    birthday: date | None = None
    created_at: datetime
    updated_at: datetime
