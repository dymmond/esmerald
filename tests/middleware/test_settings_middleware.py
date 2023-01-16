from starlette.middleware import Middleware as StarletteMiddleware

from esmerald import Gateway, JSONResponse, Request, get, settings, status
from esmerald.middleware import SettingsMiddleware
from esmerald.testclient import create_client


@get("/")
async def home(request: Request) -> None:
    assert request.settings.app_name == "test_client"

    return JSONResponse({"app_name": request.settings.app_name})


def test_assertation_error_on_missing_middleware():
    with create_client(routes=[Gateway(handler=home)]) as client:

        response = client.get("/")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "SettingsMiddleware must be added to the middlewares" in response.text


def test_request_settings():
    """
    When settings middleware is added, request can access the main settings object.
    """
    with create_client(
        routes=[Gateway(handler=home)],
        middleware=[StarletteMiddleware(SettingsMiddleware, settings=settings)],
    ) as client:
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["app_name"] == settings.app_name
