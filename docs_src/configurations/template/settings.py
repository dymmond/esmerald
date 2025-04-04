from pathlib import Path

from esmerald import EsmeraldAPISettings
from esmerald.core.config.template import TemplateConfig
from esmerald.template.jinja import JinjaTemplateEngine


class CustomSettings(EsmeraldAPISettings):
    @property
    def template_config(self) -> TemplateConfig:
        """
        Initial Default configuration for the StaticFilesConfig.
        This can be overwritten in another setting or simply override
        `template_config` or then override the `def template_config()`
        property to change the behavior of the whole template_config.

        Esmerald can also support other engines like mako, Diazo,
        Cheetah. Currently natively only supports jinja2 as its
        a standards in the market.
        """
        return TemplateConfig(
            directory=Path("templates"),
            engine=JinjaTemplateEngine,
        )
