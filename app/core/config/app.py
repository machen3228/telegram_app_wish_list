from pydantic import BaseModel


class AppConfig(BaseModel):
    max_tg_token_age: int = 86400
