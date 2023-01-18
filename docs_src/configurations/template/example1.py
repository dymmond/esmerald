from esmerald import Esmerald, TemplateConfig
from esmerald.template import JinjaTemplateEngine

from pathlib import Path


template_config = TemplateConfig(
    directory=Path("templates"),
    engine=JinjaTemplateEngine,
)

app = Esmerald(template_config=template_config)
