from pathlib import Path

from esmerald import EsmeraldSettings
from esmerald.core.config.template import TemplateConfig


class CustomSettings(EsmeraldSettings):
    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(
            directory=Path("templates"),
            env_options={"enable_async": True},
        )
