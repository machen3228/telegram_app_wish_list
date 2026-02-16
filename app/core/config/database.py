from pydantic import BaseModel
from pydantic import SecretStr
from sqlalchemy import URL


class DatabaseConfig(BaseModel):
    host: str
    port: int
    name: str
    user: str
    password: SecretStr

    # engine settings
    echo: bool = True
    pool_size: int = 10
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    pool_reset_on_return: str = 'rollback'

    # session settings
    expire_on_commit: bool = False
    autoflush: bool = True

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
