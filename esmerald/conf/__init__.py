import os
from functools import lru_cache
from typing import TYPE_CHECKING, Any, Optional, Type

from lilya._internal._module_loading import import_string

from esmerald.utils.functional import LazyObject, empty

if TYPE_CHECKING:
    from esmerald.conf.global_settings import EsmeraldAPISettings

ENVIRONMENT_VARIABLE = "ESMERALD_SETTINGS_MODULE"


@lru_cache
def reload_settings() -> Type["EsmeraldAPISettings"]:
    """
    Reloads the global settings.
    """
    settings_module: str = os.environ.get(
        ENVIRONMENT_VARIABLE, "esmerald.conf.global_settings.EsmeraldAPISettings"
    )
    settings: Type["EsmeraldAPISettings"] = import_string(settings_module)
    return settings


class EsmeraldLazySettings(LazyObject):
    """
    A lazy proxy for either global Esmerald settings or a custom settings object.
    The user can manually configure settings prior to using them. Otherwise,
    Esmerald uses the settings module pointed to by ESMERALD_SETTINGS_MODULE.
    """

    def _setup(self, name: Optional[str] = None) -> None:
        """
        Load the settings module pointed to by the environment variable. This
        is used the first time settings are needed, if the user hasn't
        configured settings manually.
        """
        settings: Type["EsmeraldAPISettings"] = reload_settings()

        for setting, _ in settings().model_dump().items():
            assert setting.islower(), "%s should be in lowercase." % setting

        self._wrapped = settings()

    def configure(self, override_settings: Type["EsmeraldAPISettings"]) -> None:
        """
        Making sure the settings are overriden by the settings_module
        provided by a given application and therefore use it as the application
        global.
        """
        self._wrapped = override_settings

    def __repr__(self: "EsmeraldLazySettings") -> str:
        # Hardcode the class name as otherwise it yields 'Settings'.
        if self._wrapped is empty:
            return "<EsmeraldLazySettings [Unevaluated]>"
        return '<EsmeraldLazySettings "{settings_module}">'.format(
            settings_module=self._wrapped.__class__.__name__
        )

    @property
    def configured(self) -> Any:
        """Return True if the settings have already been configured."""
        return self._wrapped is not empty


settings: Type["EsmeraldAPISettings"] = EsmeraldLazySettings()  # type: ignore
__lazy_settings__: Type["EsmeraldAPISettings"] = EsmeraldLazySettings()  # type: ignore
