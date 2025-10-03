from pathlib import Path

from ravyn import Ravyn
from ravyn.core.config.template import TemplateConfig
from ravyn.template.jinja import JinjaTemplateEngine

template_config = TemplateConfig(
    directory=Path("templates"),
    engine=JinjaTemplateEngine,
)

app = Ravyn(template_config=template_config)
