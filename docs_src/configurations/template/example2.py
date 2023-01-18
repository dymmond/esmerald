from esmerald import Esmerald, TemplateConfig
from esmerald.template import MakoTemplateEngine

from pathlib import Path

template_config = TemplateConfig(
    directory=Path("static"),
    engine=MakoTemplateEngine,
)

app = Esmerald(template_config=template_config)
