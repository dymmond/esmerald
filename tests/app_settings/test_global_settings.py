import builtins
import sys
from typing import List

import pytest
from asyncz.schedulers import AsyncIOScheduler

from esmerald import CORSConfig, Esmerald, EsmeraldAPISettings
from esmerald.conf.enums import EnvironmentType

real_import = builtins.__import__


def monkey_import_importerror(name, globals=None, locals=None, fromlist=(), level=0):
    if name in ("asyncz", "asyncz.schedulers"):
        raise ImportError(f"Mocked import error {name}")
    return real_import(name, globals=globals, locals=locals, fromlist=fromlist, level=level)


class AppSettings(EsmeraldAPISettings):
    environment: str = EnvironmentType.PRODUCTION


class SchedulerClassSettings(EsmeraldAPISettings):
    enable_scheduler: bool = True


class CorsAppSettings(EsmeraldAPISettings):
    allow_origins: List[str] = ["*"]


def test_reload_false():
    app = Esmerald(routes=[], settings_module=AppSettings)

    assert app.default_settings.reload is True

    # Main settings used
    assert app.settings.reload is False


def test_routes_empty():
    app = Esmerald(routes=[], settings_module=AppSettings)

    assert app.settings.routes == []


def test_cors_config():
    app = Esmerald(routes=[], settings_module=CorsAppSettings(), allow_origins=["*"])

    assert app.default_settings.reload is True

    # Main settings used
    assert isinstance(app.settings.cors_config, CORSConfig)


def test_scheduler_class_raises_error(monkeypatch):
    monkeypatch.delitem(sys.modules, "asyncz", raising=False)
    monkeypatch.setattr(builtins, "__import__", monkey_import_importerror)

    with pytest.raises(ImportError):
        Esmerald(routes=[], settings_module=SchedulerClassSettings)


def test_scheduler_class():
    app = Esmerald(routes=[], settings_module=SchedulerClassSettings)

    assert app.settings.scheduler_class == AsyncIOScheduler
