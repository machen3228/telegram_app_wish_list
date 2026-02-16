from pydantic import BaseModel
from pydantic import SecretStr


class BotConfig(BaseModel):
    token: SecretStr
