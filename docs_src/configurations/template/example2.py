from esmerald import Esmerald, TemplateConfig
from esmerald.template import MakoTemplateEngine

template_config = TemplateConfig(
    directory="/static",
    engine=MakoTemplateEngine,
)

app = Esmerald(template_config=template_config)
