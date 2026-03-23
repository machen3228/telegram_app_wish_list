from pathlib import Path

from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.contrib.sqlalchemy.plugins import SQLAlchemyPlugin
from litestar.openapi import OpenAPIConfig
from litestar.openapi.spec import Contact

from controllers import GiftController
from controllers import UserController
from core import setup_logging
from core.config import settings
from core.database import sqlalchemy_config
from exceptions.handlers import get_exception_handlers

PARENT_DIR = Path(__file__).resolve().parent

setup_logging()


cors_config = CORSConfig(
    allow_origins=[settings.app.frontend_host],
    allow_methods=['*'],
    allow_headers=['*'],
)

app = Litestar(
    route_handlers=[UserController, GiftController],
    cors_config=cors_config,
    plugins=[SQLAlchemyPlugin(config=sqlalchemy_config)],
    exception_handlers=get_exception_handlers(),
    openapi_config=OpenAPIConfig(
        title=settings.app.title,
        version=settings.app.version,
        description=settings.app.description,
        contact=Contact(
            name=settings.app.developer_name,
            email=settings.app.developer_email,
        ),
    ),
    debug=False,
)
