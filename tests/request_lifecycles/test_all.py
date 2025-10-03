from loguru import logger

from ravyn import Gateway, Include, Request, get
from ravyn.responses import PlainText
from ravyn.testclient import create_client


async def before_path_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1
    logger.info(f"first before request: {app.state.app_request}")


async def after_path_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1

    logger.info(f"first after request: {app.state.app_request}")


async def before_gateway_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1
    logger.info(f"second before request: {app.state.app_request}")


async def after_gateway_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1

    logger.info(f"second after request: {app.state.app_request}")


async def before_include_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1
    logger.info(f"third before request: {app.state.app_request}")


async def after_include_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1

    logger.info(f"third after request: {app.state.app_request}")


async def before_app_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request = 1
    logger.info(f"forth before request: {app.state.app_request}")


async def after_app_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1

    logger.info(f"forth after request: {app.state.app_request}")


def test_all_layers_request():
    @get(
        "/",
        before_request=[before_path_request],
        after_request=[after_path_request],
    )
    async def index(request: Request) -> str:
        state = request.app.state
        return PlainText(f"State: {state.app_request}")

    with create_client(
        routes=[
            Include(
                "/",
                routes=[
                    Gateway(
                        "/",
                        handler=index,
                        before_request=[before_gateway_request],
                        after_request=[after_gateway_request],
                    )
                ],
                before_request=[before_include_request],
                after_request=[after_include_request],
            ),
        ],
        before_request=[before_app_request],
        after_request=[after_app_request],
    ) as client:
        response = client.get("/")

        assert response.status_code == 200
        assert response.text == "State: 4"
