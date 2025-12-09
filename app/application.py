from pathlib import Path

from controllers import ItemController, UserController
from litestar import Litestar, get
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.response import Template
from litestar.template import TemplateConfig


@get('/')
async def index() -> Template:
    return Template(template_name='index.html')


app = Litestar(
    route_handlers=[UserController, ItemController, index],
    template_config=TemplateConfig(
        directory=Path('templates'),
        engine=JinjaTemplateEngine,
    ),
    debug=True,
)
