from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, cast

from monkay import Monkay

if TYPE_CHECKING:
    from ravyn.conf.global_settings import RavynSettings

ENVIRONMENT_VARIABLE = "RAVYN_SETTINGS_MODULE"

monkay: Monkay[None, RavynSettings] = Monkay(
    globals(),
    settings_path=lambda: os.environ.get(
        ENVIRONMENT_VARIABLE, "ravyn.conf.global_settings.RavynSettings"
    ),
)


class SettingsForward:
    def __getattribute__(self, name: str) -> Any:
        return getattr(monkay.settings, name)

    def __setattr__(self, name: str, value: Any) -> None:
        return setattr(monkay.settings, name, value)


settings: RavynSettings = cast("RavynSettings", SettingsForward())


def reload_settings() -> None:
    """
    Reloads the global settings.
    """
    monkay.settings = os.environ.get(
        ENVIRONMENT_VARIABLE, "ravyn.conf.global_settings.RavynSettings"
    )
