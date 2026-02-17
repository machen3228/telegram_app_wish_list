from pathlib import Path

from litestar import Litestar
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Contact
from litestar.static_files import create_static_files_router

from controllers import GiftController
from controllers import UserController
from core.config import settings
from core.database import sqlalchemy_config

PARENT_DIR = Path(__file__).resolve().parent
STATIC_DIR = PARENT_DIR / 'static'

static_files_router = create_static_files_router(
    path='/',
    directories=[STATIC_DIR],
    html_mode=True,
)

app = Litestar(
    route_handlers=[UserController, GiftController, static_files_router],
    plugins=[SQLAlchemyPlugin(config=sqlalchemy_config)],
    openapi_config=OpenAPIConfig(
        title=settings.app.title,
        version=settings.app.version,
        description=settings.app.description,
        contact=Contact(
            name=settings.app.developer_name,
            email=settings.app.developer_email,
        ),
    ),
    debug=True,
)
