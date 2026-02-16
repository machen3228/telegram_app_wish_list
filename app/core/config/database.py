from pydantic import BaseModel
from pydantic import SecretStr
from sqlalchemy import URL


class DatabaseConfig(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: SecretStr

    echo: bool = True

    @property
    def async_url(self) -> URL:
        return URL.create(
            drivername='postgresql+asyncpg',
            database=self.name,
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password.get_secret_value(),
        )

    @property
    def test_async_url(self) -> URL:
        return URL.create(
            drivername='postgresql+asyncpg',
            database=f'{self.name}_test',
            host='localhost',
            port=self.port,
            username=self.user,
            password=self.password.get_secret_value(),
        )
