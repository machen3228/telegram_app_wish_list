from datetime import timedelta

from pydantic import BaseModel
from pydantic import SecretStr


class JWTConfig(BaseModel):
    secret_key: SecretStr
    algorithm: str = 'HS256'
    access_token_expires: timedelta = timedelta(hours=1)
