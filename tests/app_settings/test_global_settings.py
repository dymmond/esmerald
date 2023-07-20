from typing import TYPE_CHECKING

from esmerald import Esmerald, EsmeraldAPISettings
from esmerald.conf.enums import EnvironmentType

if TYPE_CHECKING:
    pass


class AppSettings(EsmeraldAPISettings):
    environment: str = EnvironmentType.PRODUCTION


def test_reload_false():
    app = Esmerald(routes=[], settings_config=AppSettings)

    assert app.default_settings.reload is True

    # Main settings used
    assert app.settings.reload is False


def test_routes_empty():
    app = Esmerald(routes=[], settings_config=AppSettings)

    assert app.settings.routes == []
