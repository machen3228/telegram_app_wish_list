from pathlib import Path

from controllers import ItemController, UserController
from litestar import Litestar, get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.response import Template
from litestar.template import TemplateConfig

ROOT = Path(__file__).resolve().parent


@get('/')
async def index() -> Template:
    return Template(template_name=str(ROOT / 'templates'))


app = Litestar(
    route_handlers=[UserController, ItemController, index],
    template_config=TemplateConfig(
        directory=[str(ROOT / 'static')],
        engine=JinjaTemplateEngine,
    ),
    debug=True,
)
