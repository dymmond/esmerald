from pathlib import Path

from ravyn import RavynSettings
from ravyn.core.config.template import TemplateConfig


class CustomSettings(RavynSettings):
    @property
    def template_config(self) -> TemplateConfig:
        return TemplateConfig(
            directory=Path("templates"),
            env_options={"enable_async": True},
        )
