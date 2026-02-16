from advanced_alchemy.extensions.litestar import AsyncSessionConfig
from advanced_alchemy.extensions.litestar import EngineConfig
from advanced_alchemy.extensions.litestar import SQLAlchemyAsyncConfig

from core.config import settings

engine_config = EngineConfig(
    echo=settings.db.engine.echo,
    pool_size=settings.db.engine.pool_size,
    max_overflow=settings.db.engine.max_overflow,
    pool_timeout=settings.db.engine.pool_timeout,
    pool_recycle=settings.db.engine.pool_recycle,
    pool_pre_ping=settings.db.engine.pool_pre_ping,
    pool_reset_on_return=settings.db.engine.pool_reset_on_return,
    connect_args={
        'server_settings': {
            'application_name': 'wish_list_app',
            'jit': 'off',
            'timezone': 'UTC',
        },
        'command_timeout': 60,
    },
)

session_config = AsyncSessionConfig(
    expire_on_commit=settings.db.session.expire_on_commit,
    autoflush=settings.db.session.autoflush,
)

sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.db.async_url.render_as_string(hide_password=False),
    session_dependency_key='db_session',
    engine_dependency_key='db_engine',
    engine_config=engine_config,
    session_config=session_config,
)
