from esmerald import Esmerald, TemplateConfig
from esmerald.template import JinjaTemplateEngine

template_config = TemplateConfig(
    directory="/static",
    engine=JinjaTemplateEngine,
)

app = Esmerald(template_config=template_config)
