from pathlib import Path

from esmerald import EsmeraldAPISettings
from esmerald.core.config.template import TemplateConfig


class CustomSettings(EsmeraldAPISettings):
    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(
            directory=Path("templates"),
            env_options={"enable_async": True},
        )
