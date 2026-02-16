from advanced_alchemy.extensions.litestar import AsyncSessionConfig
from advanced_alchemy.extensions.litestar import EngineConfig
from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig

from core.config import settings

sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.db.async_url.render_as_string(hide_password=False),
    session_dependency_key='db_session',
    engine_dependency_key='db_engine',
    engine_config=EngineConfig(
        echo=settings.db.echo,
        pool_size=settings.db.pool_size,
        max_overflow=settings.db.max_overflow,
        pool_timeout=settings.db.pool_timeout,
        pool_recycle=settings.db.pool_recycle,
        pool_pre_ping=settings.db.pool_pre_ping,
        pool_reset_on_return=settings.db.pool_reset_on_return,
        connect_args={
            'server_settings': {
                'application_name': 'wish_list_app',
                'jit': 'off',
                'timezone': 'UTC',
            },
            'command_timeout': 60,
        },
    ),
    session_config=AsyncSessionConfig(
        expire_on_commit=settings.db.expire_on_commit,
        autoflush=settings.db.autoflush,
    ),
)
