from ravyn import Gateway, Include, JSONResponse, Ravyn, RavynSettings, get, settings
from ravyn.conf import monkay
from ravyn.testclient import create_client


@get()
async def home() -> JSONResponse:
    return JSONResponse({"title": settings.title, "debug": settings.debug})


@get()
async def home_unset() -> JSONResponse:
    with monkay.with_settings(None):
        return JSONResponse({"title": settings.title, "debug": settings.debug})


class NewSettings(RavynSettings):
    title: str = "Settings being parsed by the middleware and make it app global"
    debug: bool = False


class NestedAppSettings(RavynSettings):
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


def test_app_settings_middleware_nested_with_child_ravyn(test_client_factory):
    with create_client(
        settings_module=NewSettings,
        routes=[
            Gateway("/home", handler=home),
            Include(
                "/child",
                app=Ravyn(
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


def test_app_settings_middleware_nested_with_child_ravyn_and_global(test_client_factory):
    with create_client(
        settings_module=NewSettings,
        routes=[
            Gateway("/home", handler=home),
            Include(
                "/child",
                app=Ravyn(
                    settings_module=NestedAppSettings,
                    routes=[
                        Gateway("/home", handler=home),
                    ],
                ),
            ),
            Include(
                "/another-child",
                app=Ravyn(
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
        assert response.json() == {"title": "Ravyn", "debug": False}
