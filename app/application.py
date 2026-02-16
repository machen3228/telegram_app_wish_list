from pathlib import Path

from litestar import Litestar
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyAsyncConfig
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Contact
from litestar.static_files import create_static_files_router

from controllers import GiftController
from controllers import UserController
from core.config import settings

PARENT_DIR = Path(__file__).resolve().parent
STATIC_DIR = PARENT_DIR / 'static'

sqlalchemy_config = SQLAlchemyAsyncConfig(
    connection_string=settings.db.async_url.render_as_string(hide_password=False),
    session_dependency_key='db_session',
)

static_files_router = create_static_files_router(
    path='/',
    directories=[STATIC_DIR],
    html_mode=True,
)

app = Litestar(
    route_handlers=[UserController, GiftController, static_files_router],
    plugins=[SQLAlchemyPlugin(config=sqlalchemy_config)],
    openapi_config=OpenAPIConfig(
        title='Wishlist API',
        version='0.0.1',
        description='Backend API for Telegram wishlist app',
        contact=Contact(
            name='developer',
            email='machen3228@gmail.com',
        ),
    ),
    debug=True,
)
