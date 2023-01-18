from esmerald import EsmeraldAPISettings, TemplateConfig
from esmerald.template import JinjaTemplateEngine

from pathlib import Path

class CustomSettings(EsmeraldAPISettings):
    @property
    def template_config(self) -> TemplateConfig:
        """
        Initial Default configuration for the StaticFilesConfig.
        This can be overwritten in another setting or simply override
        `template_config` or then override the `def template_config()`
        property to change the behavior of the whole template_config.

        Esmerald can also support other engines like mako, Diazo,
        Cheetah. Currently natively only supports jinja2 and mako as they
        are standards in the market.
        """
        return TemplateConfig(
            directory=Path("templates"),
            engine=JinjaTemplateEngine,
        )
