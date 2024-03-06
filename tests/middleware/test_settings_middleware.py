from lilya.middleware import DefineMiddleware

from esmerald import Gateway, JSONResponse, Request, get, settings, status
from esmerald.middleware import RequestSettingsMiddleware
from esmerald.testclient import create_client


@get("/")
async def home(request: Request) -> None:
    assert request.global_settings.app_name == "test_client"

    return JSONResponse({"app_name": request.global_settings.app_name})


def test_assertation_error_on_missing_middleware(test_client_factory):
    with create_client(routes=[Gateway(handler=home)]) as client:
        response = client.get("/")
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "RequestSettingsMiddleware must be added to the middlewares" in response.text


def test_request_settings_default(test_client_factory):
    """
    When settings middleware is added without settings param, request can access the main settings object.
    """
    with create_client(
        routes=[Gateway(handler=home)],
        middleware=[DefineMiddleware(RequestSettingsMiddleware)],
    ) as client:
        response = client.get("/")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["app_name"] == settings.app_name
