from typing import Optional

import pytest
from loguru import logger
from pydantic import BaseModel

from esmerald import Esmerald, Extension, Pluggable
from esmerald.exceptions import ImproperlyConfigured


class MyNewPluggable:
    ...


class PluggableNoPlug(Extension):
    def __init__(self, app: "Esmerald"):
        super().__init__(app)
        self.app = app


def test_raises_improperly_configured_for_subsclass(test_client_factory):
    with pytest.raises(ImproperlyConfigured) as raised:
        Esmerald(routes=[], pluggables={"test": MyNewPluggable})

    assert raised.value.detail == "An extension must subclass from esmerald.pluggables.Extension"


def test_raises_improperly_configured_for_key_of_pluggables(test_client_factory):
    with pytest.raises(ImproperlyConfigured) as raised:
        Esmerald(routes=[], pluggables={1: MyNewPluggable})

    assert raised.value.detail == "Pluggable names should be in string format."


def test_raises_error_for_missing_extend(test_client_factory):
    with pytest.raises(Exception) as raised:
        Esmerald(
            routes=[],
            pluggables={"test": Pluggable(PluggableNoPlug)},
        )

    assert (
        raised.value.args[0]
        == "Can't instantiate abstract class PluggableNoPlug with abstract method extend"
    )


class Config(BaseModel):
    name: Optional[str]


class MyExtension(Extension):
    def __init__(self, app: "Esmerald", config: Config):
        super().__init__(app)
        self.app = app
        self.config = config

    def extend(self, config: Config) -> None:
        logger.info(f"Started extension with config name {config.name}")


def test_generates_pluggable():
    app = Esmerald(
        routes=[], pluggables={"test": Pluggable(MyExtension, config=Config(name="my pluggable"))}
    )

    assert "test" in app.pluggables


def test_generates_many_pluggables():
    class LoggingExtension(Extension):
        def __init__(self, app: "Esmerald", name):
            super().__init__(app)
            self.app = app
            self.name = name

        def extend(self, name) -> None:
            logger.info(f"Started logging extension with name {name}")

    class DatabaseExtension(Extension):
        def __init__(self, app: "Esmerald", database):
            super().__init__(app)
            self.app = app
            self.database = database

        def extend(self, database) -> None:
            logger.info(f"Started extension with database {database}")

    app = Esmerald(
        routes=[],
        pluggables={
            "test": Pluggable(MyExtension, config=Config(name="my pluggable")),
            "logging": Pluggable(LoggingExtension, name="my logging"),
            "database": Pluggable(DatabaseExtension, database="my db"),
        },
    )

    assert len(app.pluggables.keys()) == 3
