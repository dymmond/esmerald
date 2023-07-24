import builtins
import sys

import pytest
from asyncz.schedulers import AsyncIOScheduler

from esmerald.testclient import create_client

real_import = builtins.__import__


def monkey_import_importerror(name, globals=None, locals=None, fromlist=(), level=0):
    if name in (
        "asyncz",
        "asyncz.contrib",
        "asyncz.contrib.esmerald",
        "asyncz.contrib.esmerald.scheduler",
    ):
        raise ImportError(f"Mocked import error {name}")
    return real_import(name, globals=globals, locals=locals, fromlist=fromlist, level=level)


def test_default_scheduler(test_client_factory):
    with create_client([], enable_scheduler=True, scheduler_class=AsyncIOScheduler) as client:
        app = client.app

        assert app.scheduler_class == AsyncIOScheduler


def test_raises_import_error_on_missing_module(monkeypatch):
    monkeypatch.delitem(sys.modules, "asyncz", raising=False)
    monkeypatch.setattr(builtins, "__import__", monkey_import_importerror)

    with pytest.raises(ImportError):
        with create_client([], enable_scheduler=True, scheduler_class=AsyncIOScheduler):
            """ """
