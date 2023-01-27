from pathlib import Path

from esmerald import Esmerald
from esmerald.config.template import TemplateConfig
from esmerald.template.mako import MakoTemplateEngine

template_config = TemplateConfig(
    directory=Path("templates"),
    engine=MakoTemplateEngine,
)

app = Esmerald(template_config=template_config)
