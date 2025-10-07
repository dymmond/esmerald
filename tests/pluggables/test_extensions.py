from typing import Optional

import pytest
from loguru import logger
from pydantic import BaseModel

from ravyn import Extension, Pluggable, Ravyn
from ravyn.exceptions import ImproperlyConfigured
from ravyn.types import DictAny


class MyNewPluggable: ...


class PluggableNoPlug(Extension):  # pragma: no cover
    def __init__(self, app: "Ravyn"):
        super().__init__(app)
        self.app = app


def test_raises_improperly_configured_for_subclass(test_client_factory):
    with pytest.raises(ImproperlyConfigured) as raised:
        Ravyn(routes=[], extensions={"test": MyNewPluggable})

    assert raised.value.detail == (
        "An extension must subclass from Extension, implement the ExtensionProtocol "
        "as instance or being wrapped in a Pluggable."
    )


def test_raises_improperly_configured_for_key_of_pluggables(test_client_factory):
    with pytest.raises(ImproperlyConfigured) as raised:
        Ravyn(routes=[], extensions={1: MyNewPluggable})

    assert raised.value.detail == "Extension names should be in string format."


def test_raises_error_for_missing_extend(test_client_factory):
    with pytest.raises(Exception):  # noqa
        Ravyn(
            routes=[],
            extensions={"test": Pluggable(PluggableNoPlug)},
        )


class Config(BaseModel):
    name: Optional[str]


class MyExtension(Extension):
    def __init__(self, app: "Ravyn", config: Config):
        super().__init__(app)
        self.config = config

    def extend(self, config: Config) -> None:
        logger.info(f"Started extension with config name {config.name}")


def test_generates_pluggable():
    app = Ravyn(
        routes=[],
        extensions={
            "test": Pluggable(MyExtension, config=Config(name="my pluggable")),
            "test2": Pluggable("tests.pluggables.import_target.MyExtension2"),
            "test3": "tests.pluggables.import_target.MyExtension2",
        },
    )

    assert "test" in app.extensions
    assert isinstance(app.extensions["test"], Extension)
    assert "test2" in app.extensions
    assert isinstance(app.extensions["test2"], Extension)
    assert "test3" in app.extensions
    assert isinstance(app.extensions["test3"], Extension)


def test_generates_many_pluggables():
    container = []

    class ReorderedExtension(Extension):
        def __init__(self, app: "Ravyn"):
            super().__init__(app)

        def extend(self) -> None:
            container.append("works")

    class NonExtension:
        def __init__(self, app: "Ravyn"):
            super().__init__()
            self.app = app

        def extend(self) -> None:
            pass

    class LoggingExtension(Extension):
        def __init__(self, app: "Ravyn", name):
            super().__init__(app)
            self.name = name

        def extend(self, name) -> None:
            self.app.extensions.ensure_extension("base")
            assert container == ["works"]
            logger.info(f"Started logging extension with name {name}")

    class DatabaseExtension(Extension):
        def __init__(self, app: "Ravyn", database):
            super().__init__(app)
            self.database = database

        def extend(self, database) -> None:
            with pytest.raises(ValueError):
                self.app.extensions.ensure_extension("non-existing")
            logger.info(f"Started extension with database {database}")

    app = Ravyn(
        routes=[],
        extensions={
            "test": Pluggable(MyExtension, config=Config(name="my pluggable")),
            "logging": Pluggable(LoggingExtension, name="my logging"),
            "database": Pluggable(DatabaseExtension, database="my db"),
            "base": ReorderedExtension,
            "non-extension": NonExtension,
        },
    )

    assert len(app.extensions.keys()) == 5


def test_start_extension_directly(test_client_factory):
    class CustomExtension(Extension):
        def __init__(self, app: Optional["Ravyn"] = None, **kwargs: DictAny):
            super().__init__(app, **kwargs)

        def extend(self, **kwargs) -> None:
            app = kwargs.get("app")
            config = kwargs.get("config")
            logger.success(f"Started standalone plugging with the name: {config.name}")
            app.extensions["custom"] = self

    app = Ravyn(routes=[])
    config = Config(name="standalone")
    extension = CustomExtension()
    extension.extend(app=app, config=config)

    assert "custom" in app.extensions
    assert isinstance(app.extensions["custom"], Extension)


def test_add_extension_manual(test_client_factory):
    class CustomExtension(Extension):
        def __init__(self, app: Optional["Ravyn"] = None, **kwargs: DictAny):
            super().__init__(app, **kwargs)
            self.app = app

        def extend(self, config) -> None:
            logger.success(f"Started plugging with the name: {config.name}")

            self.app.add_extension("manual", self)

    app = Ravyn(routes=[])
    config = Config(name="manual")
    extension = CustomExtension(app=app)
    extension.extend(config=config)

    assert "manual" in app.extensions
    assert isinstance(app.extensions["manual"], Extension)


def test_add_standalone_extension(test_client_factory):
    class CustomExtension:
        def __init__(self, app: Optional["Ravyn"] = None, **kwargs: DictAny):
            self.app = app
            self.kwargs = kwargs

        def extend(self, config) -> None:
            logger.success(f"Started standalone plugging with the name: {config.name}")

            self.app.add_extension("manual", self)

    app = Ravyn(routes=[])
    config = Config(name="manual")
    extension = CustomExtension(app=app)
    extension.extend(config=config)

    assert "manual" in app.extensions
    assert not isinstance(app.extensions["manual"], Extension)


def test_add_extension(test_client_factory):
    class CustomExtension(Extension):
        def __init__(self, app: Optional["Ravyn"] = None, **kwargs: DictAny):
            super().__init__(app, **kwargs)
            self.app = app

        def extend(self, config) -> None:
            logger.success(f"Started standalone plugging with the name: {config.name}")

    app = Ravyn(routes=[])
    config = Config(name="manual")
    app.add_extension("manual", Pluggable(CustomExtension, config=config))

    assert "manual" in app.extensions
    assert isinstance(app.extensions["manual"], Extension)
