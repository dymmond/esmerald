from esmerald import Esmerald, EsmeraldAPISettings, Gateway, Include, JSONResponse, get, settings
from esmerald.conf import monkay
from esmerald.testclient import create_client


@get()
async def home() -> JSONResponse:
    return JSONResponse({"title": settings.title, "debug": settings.debug})


@get()
async def home_unset() -> JSONResponse:
    with monkay.with_settings(None):
        return JSONResponse({"title": settings.title, "debug": settings.debug})


class NewSettings(EsmeraldAPISettings):
    title: str = "Settings being parsed by the middleware and make it app global"
    debug: bool = False


class NestedAppSettings(EsmeraldAPISettings):
    title: str = "Nested app title"
    debug: bool = True


def test_app_settings_middleware(test_client_factory):
    with create_client(
        settings_module=NewSettings,
        routes=[Gateway("/home", handler=home)],
    ) as client:
        response = client.get("/home")

        assert response.json() == {
            "title": "Settings being parsed by the middleware and make it app global",
            "debug": False,
        }


def test_app_settings_middleware_nested_with_child_esmerald(test_client_factory):
    with create_client(
        settings_module=NewSettings,
        routes=[
            Gateway("/home", handler=home),
            Include(
                "/child",
                app=Esmerald(
                    settings_module=NestedAppSettings,
                    routes=[
                        Gateway("/home", handler=home),
                    ],
                ),
            ),
        ],
    ) as client:
        response = client.get("/home")

        assert response.json() == {
            "title": "Settings being parsed by the middleware and make it app global",
            "debug": False,
        }

        response = client.get("/child/home")

        assert response.json() == {"title": "Nested app title", "debug": True}


def test_app_settings_middleware_nested_with_child_esmerald_and_global(test_client_factory):
    with create_client(
        settings_module=NewSettings,
        routes=[
            Gateway("/home", handler=home),
            Include(
                "/child",
                app=Esmerald(
                    settings_module=NestedAppSettings,
                    routes=[
                        Gateway("/home", handler=home),
                    ],
                ),
            ),
            Include(
                "/another-child",
                app=Esmerald(
                    routes=[
                        Gateway("/home", handler=home),
                        Gateway("/unset", handler=home_unset),
                    ],
                ),
            ),
        ],
    ) as client:
        response = client.get("/home")

        assert response.json() == {
            "title": "Settings being parsed by the middleware and make it app global",
            "debug": False,
        }

        response = client.get("/child/home")

        assert response.json() == {"title": "Nested app title", "debug": True}

        response = client.get("/another-child/home")

        # should be propagated
        assert response.json() == {
            "title": "Settings being parsed by the middleware and make it app global",
            "debug": False,
        }

        # should use the defaults
        response = client.get("/another-child/unset")
        assert response.json() == {"title": "Esmerald", "debug": False}
