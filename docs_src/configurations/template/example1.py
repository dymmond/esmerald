from pathlib import Path

from esmerald import Esmerald
from esmerald.config.template import TemplateConfig
from esmerald.template.jinja import JinjaTemplateEngine

template_config = TemplateConfig(
    directory=Path("templates"),
    engine=JinjaTemplateEngine,
)

app = Esmerald(template_config=template_config)
