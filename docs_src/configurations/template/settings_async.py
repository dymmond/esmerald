from pathlib import Path

from esmerald import EsmeraldAPISettings
from esmerald.config.template import TemplateConfig
from esmerald.template.jinja import JinjaTemplateEngine


class CustomSettings(EsmeraldAPISettings):
    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(
            directory=Path("templates"),
            env_options={"enable_async": True},
        )
