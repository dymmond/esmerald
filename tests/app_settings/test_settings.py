import json
from typing import Any, Dict, List

import pytest
from lilya.middleware import DefineMiddleware
from pydantic import BaseModel

from esmerald import (
    ChildEsmerald,
    Esmerald,
    EsmeraldAPISettings,
    Gateway,
    Include,
    JSONResponse,
    Request,
    get,
    settings,
)
from esmerald.config import CORSConfig, CSRFConfig
from esmerald.exceptions import ImproperlyConfigured
from esmerald.middleware import RequestSettingsMiddleware
from esmerald.testclient import create_client
from esmerald.types import Middleware
from esmerald.utils.crypto import get_random_secret_key


def test_main_settings():
    with create_client([]) as client:
        assert client.app.settings.app_name == settings.app_name
        assert client.app.settings.environment == "testing"
        assert client.app.settings.debug == settings.debug
        assert client.app.settings.allowed_hosts == settings.allowed_hosts
        assert client.app.settings.enable_sync_handlers == settings.enable_sync_handlers
        assert client.app.settings.enable_openapi == settings.enable_openapi
        assert client.app.settings.allow_origins == settings.allow_origins
        assert client.app.settings.on_shutdown == settings.on_shutdown
        assert client.app.settings.on_startup == settings.on_startup
        assert client.app.settings.on_startup == settings.on_startup
        assert client.app.settings.lifespan == settings.lifespan
        assert client.app.settings.on_startup == settings.on_startup
        assert client.app.settings.version == settings.version
        assert client.app.settings.secret_key == settings.secret_key
        assert client.app.settings.response_class == settings.response_class
        assert client.app.settings.response_cookies == settings.response_cookies
        assert client.app.settings.tags == settings.tags
        assert client.app.settings.include_in_schema == settings.include_in_schema
        assert client.app.settings.scheduler_class == settings.scheduler_class
        assert client.app.settings.reload == settings.reload
        assert client.app.settings.password_hashers == settings.password_hashers
        assert client.app.settings.csrf_config == settings.csrf_config
        assert client.app.settings.async_exit_config == settings.async_exit_config
        assert client.app.settings.template_config == settings.template_config
        assert client.app.settings.static_files_config == settings.static_files_config
        assert client.app.settings.cors_config == settings.cors_config
        assert client.app.settings.session_config == settings.session_config
        assert client.app.settings.openapi_config == settings.openapi_config
        assert client.app.settings.middleware == settings.middleware
        assert client.app.settings.permissions == settings.permissions
        assert client.app.settings.dependencies == settings.dependencies
        assert client.app.settings.exception_handlers == settings.exception_handlers
        assert client.app.settings.redirect_slashes == settings.redirect_slashes


class DummySettings(BaseModel):
    app_name: str = "test"


class DummyObject: ...


@get("/request-settings")
async def _request_settings(request: Request) -> JSONResponse:
    return JSONResponse(
        {
            "global_settings": request.global_settings.app_name,
        }
    )


@get("/app-settings")
async def _app_settings(request: Request) -> str:
    return request.app.settings.app_name


class DisableOpenAPI(EsmeraldAPISettings):
    enable_openapi: bool = True


def test_settings_global(test_client_factory):
    """
    Tests settings are setup properly
    """
    with create_client(
        app_name="my app",
        routes=[Gateway(handler=_request_settings), Gateway(handler=_app_settings)],
        middleware=[DefineMiddleware(RequestSettingsMiddleware)],
    ) as client:
        request_settings = client.get("/request-settings")
        app_settings = client.get("/app-settings")

        assert client.app.app_name == "my app"
        assert settings.app_name == "test_client"
        assert request_settings.json()["global_settings"] == "test_client"
        assert app_settings.json() == "test_client"


def test_settings_global_without_parameters(test_client_factory):
    with create_client(
        routes=[Gateway(handler=_request_settings), Gateway(handler=_app_settings)],
        middleware=[DefineMiddleware(RequestSettingsMiddleware)],
    ) as client:
        request_settings = client.get("/request-settings")
        app_settings = client.get("/app-settings")

        assert settings.app_name == "test_client"
        assert client.app.app_name == "test_client"
        assert request_settings.json()["global_settings"] == "test_client"
        assert app_settings.json() == "test_client"


def test_inner_settings_config(test_client_factory):
    """
    Test passing a settings config and being used with teh ESMERALD_SETTINGS_MODULE
    """

    class AppSettings(DisableOpenAPI):
        app_name: str = "new app"
        allowed_hosts: List[str] = ["*", "*.testserver.com"]

        @property
        def middleware(self) -> List["Middleware"]:
            return [RequestSettingsMiddleware]

    @get("/app-settings")
    async def _app_settings(request: Request) -> str:
        return JSONResponse(
            {"middleware": [middleware.__name__ for middleware in request.app.settings.middleware]}
        )

    with create_client(
        routes=[Gateway(handler=_app_settings)], settings_module=AppSettings
    ) as client:
        response = client.get("/app-settings")
        assert client.app.settings.app_name == "new app"
        assert client.app.app_name == "new app"
        assert settings.app_name == "test_client"
        assert "RequestSettingsMiddleware" == response.json()["middleware"][0]
        assert isinstance(client.app.settings_module, EsmeraldAPISettings)


def test_inner_settings_config_as_instance(test_client_factory):
    """
    Test passing a settings config and being used with teh ESMERALD_SETTINGS_MODULE
    """

    class AppSettings(DisableOpenAPI):
        app_name: str = "new app"
        allowed_hosts: List[str] = ["*", "*.testserver.com"]

        @property
        def middleware(self) -> List["Middleware"]:
            return [RequestSettingsMiddleware]

    @get("/app-settings")
    async def _app_settings(request: Request) -> str:
        return JSONResponse(
            {"middleware": [middleware.__name__ for middleware in request.app.settings.middleware]}
        )

    with create_client(
        routes=[Gateway(handler=_app_settings)], settings_module=AppSettings()
    ) as client:
        response = client.get("/app-settings")

        assert client.app.settings.app_name == "new app"
        assert client.app.app_name == "new app"
        assert settings.app_name == "test_client"
        assert "RequestSettingsMiddleware" == response.json()["middleware"][0]
        assert isinstance(client.app.settings_module, EsmeraldAPISettings)


def test_child_esmerald_independent_settings(test_client_factory):
    """
    Tests that a ChildEsmerald can have indepedent settings module
    """

    class ChildSettings(DisableOpenAPI):
        app_name: str = "child app"
        secret_key: str = "child key"

    @get("/app-settings")
    async def _app_settings(request: Request) -> Dict[Any, Any]:
        return request.app_settings.model_dump_json()

    child = ChildEsmerald(
        routes=[Gateway(handler=_app_settings)],
        settings_module=ChildSettings,
        middleware=[DefineMiddleware(RequestSettingsMiddleware)],
    )

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.get("/child/app-settings")
        data = json.loads(response.json())

        assert data["app_name"] == "child app"
        assert data["secret_key"] == "child key"
        assert child.app_name == "child app"
        assert child.secret_key == "child key"
        assert client.app.app_name == settings.app_name


def test_child_esmerald_independent_cors_config(test_client_factory):
    """
    Tests that a ChildEsmerald can have indepedent settings module
    """
    cors_config = CORSConfig(allow_origins=["*"])
    csrf_config = CSRFConfig(secret=settings.secret_key)

    class ChildSettings(DisableOpenAPI):
        app_name: str = "child app"
        secret_key: str = "child key"

        @property
        def cors_config(self) -> CORSConfig:
            return CORSConfig(allow_origins=["www.example.com"])

    @get("/app-settings")
    async def _app_settings(request: Request) -> Dict[Any, Any]:
        return request.app_settings.model_dump_json()  # pragma: no cover

    secret = get_random_secret_key()
    child = ChildEsmerald(
        routes=[Gateway(handler=_app_settings)],
        settings_module=ChildSettings,
        middleware=[DefineMiddleware(RequestSettingsMiddleware)],
        csrf_config=CSRFConfig(secret=secret),
    )

    with create_client(
        routes=[Include("/child", app=child)], cors_config=cors_config, csrf_config=csrf_config
    ) as client:
        child = client.app.routes[0].app

        assert child.cors_config.allow_origins == ["www.example.com"]
        assert child.csrf_config.secret == secret
        assert client.app.cors_config.allow_origins == ["*"]
        assert client.app.csrf_config.secret == settings.secret_key


def test_nested_child_esmerald_independent_settings(test_client_factory):
    """
    Tests that a nested ChildEsmerald can have indepedent settings module
    """

    class NestedChildSettings(DisableOpenAPI):
        app_name: str = "nested child app"
        secret_key: str = "nested child key"

    class ChildSettings(DisableOpenAPI):
        app_name: str = "child app"
        secret_key: str = "child key"

    @get("/app-settings")
    async def _app_settings(request: Request) -> Dict[Any, Any]:
        return request.app_settings.model_dump_json()

    child = ChildEsmerald(
        routes=[Gateway(handler=_app_settings)],
        settings_module=NestedChildSettings,
        middleware=[DefineMiddleware(RequestSettingsMiddleware)],
    )

    nested_child = ChildEsmerald(routes=[Include(app=child)], settings_module=ChildSettings)

    with create_client(
        routes=[Include("/child", app=nested_child)],
    ) as client:
        response = client.get("/child/app-settings")
        data = json.loads(response.json())

        _child = client.app.routes[0].app

        assert data["app_name"] == "nested child app"
        assert data["secret_key"] == "nested child key"
        assert nested_child.app_name == "child app"
        assert nested_child.secret_key == "child key"

        assert _child.app_name == "child app"
        assert _child.secret_key == "child key"

        assert client.app.app_name == settings.app_name


@pytest.mark.parametrize("settings_module", [Esmerald, ChildEsmerald, DummySettings, DummyObject])
def test_raises_exception_on_wrong_settings(settings_module, test_client_factory):
    """If a settings_module is thrown but not type EsmeraldAPISettings"""
    with pytest.raises(ImproperlyConfigured):
        with create_client(routes=[], settings_module=settings_module):
            """ """


def test_basic_settings(test_client_factory):
    app = Esmerald(
        debug=False,
        enable_scheduler=False,
        include_in_schema=False,
        enable_openapi=False,
        redirect_slashes=False,
    )

    assert app.debug is False
    assert app.enable_scheduler is False
    assert app.include_in_schema is False
    assert app.enable_openapi is False
    assert app.redirect_slashes is False


def test_default_settings():
    app = Esmerald(
        debug=False,
        enable_scheduler=False,
        include_in_schema=False,
        enable_openapi=False,
        redirect_slashes=False,
    )

    assert id(app.default_settings) == id(settings)
