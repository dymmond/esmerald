import json
from typing import Any, Dict, List

from lilya.middleware import DefineMiddleware
from pydantic import BaseModel

from esmerald import (
    ChildEsmerald,
    EsmeraldSettings,
    Gateway,
    Include,
    JSONResponse,
    Request,
    get,
    settings,
)
from esmerald.core.config import CORSConfig, CSRFConfig
from esmerald.middleware import RequestSettingsMiddleware
from esmerald.testclient import create_client
from esmerald.types import Middleware
from esmerald.utils.crypto import get_random_secret_key


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


class DisableOpenAPI(EsmeraldSettings):
    enable_openapi: bool = True


def test_settings_global(test_client_factory):
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


class AppSettings(DisableOpenAPI):
    app_name: str = "new app"
    allowed_hosts: List[str] = ["*", "*.testserver.com"]

    @property
    def middleware(self) -> List["Middleware"]:
        return [RequestSettingsMiddleware]


def test_inner_settings_module(test_client_factory):
    @get("/app-settings")
    async def _app_settings(request: Request) -> str:
        return JSONResponse(
            {"middleware": [middleware.__name__ for middleware in request.app.settings.middleware]}
        )

    with create_client(
        routes=[Gateway(handler=_app_settings)],
        settings_module="tests.app_settings.test_settings_module_string.AppSettings",
    ) as client:
        response = client.get("/app-settings")
        assert client.app.settings.app_name == "new app"
        assert client.app.app_name == "new app"
        assert settings.app_name == "test_client"
        assert "RequestSettingsMiddleware" == response.json()["middleware"][0]
        assert isinstance(client.app.settings_module, EsmeraldSettings)


class ChildSettings(DisableOpenAPI):
    app_name: str = "child app"
    secret_key: str = "child key"


def test_child_esmerald_independent_settings(test_client_factory):
    @get("/app-settings")
    async def _app_settings(request: Request) -> Dict[Any, Any]:
        return request.app_settings.model_dump_json(exclude={"cache_backend"})  # pragma: no cover

    child = ChildEsmerald(
        routes=[Gateway(handler=_app_settings)],
        settings_module="tests.app_settings.test_settings_module_string.ChildSettings",
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


class ChildSettingCors(DisableOpenAPI):
    app_name: str = "child app"
    secret_key: str = "child key"

    @property
    def cors_config(self) -> CORSConfig:
        return CORSConfig(allow_origins=["www.example.com"])


def test_child_esmerald_independent_cors_config(test_client_factory):
    cors_config = CORSConfig(allow_origins=["*"])
    csrf_config = CSRFConfig(secret=settings.secret_key)

    @get("/app-settings")
    async def _app_settings(request: Request) -> Dict[Any, Any]:
        return request.app_settings.model_dump_json(
            exclude={"cache_backend"}
        )  # pragma: no cover  # pragma: no cover

    secret = get_random_secret_key()
    child = ChildEsmerald(
        routes=[Gateway(handler=_app_settings)],
        settings_module="tests.app_settings.test_settings_module_string.ChildSettingCors",
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


class NestedChildSettings(DisableOpenAPI):
    app_name: str = "nested child app"
    secret_key: str = "nested child key"


def test_nested_child_esmerald_independent_settings(test_client_factory):
    @get("/app-settings")
    async def _app_settings(request: Request) -> Dict[Any, Any]:
        return request.app_settings.model_dump_json(exclude={"cache_backend"})  # pragma: no cover

    child = ChildEsmerald(
        routes=[Gateway(handler=_app_settings)],
        settings_module="tests.app_settings.test_settings_module_string.NestedChildSettings",
        middleware=[DefineMiddleware(RequestSettingsMiddleware)],
    )

    nested_child = ChildEsmerald(
        routes=[Include(app=child)],
        settings_module="tests.app_settings.test_settings_module_string.ChildSettings",
    )

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
