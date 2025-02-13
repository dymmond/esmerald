from loguru import logger

from esmerald import Gateway, Include, Request, get
from esmerald.responses import PlainText
from esmerald.testclient import create_client


async def before_path_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1
    logger.info(f"Before path request: {app.state.app_request}")


async def after_path_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1

    logger.info(f"After path request: {app.state.app_request}")


async def before_include_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1
    logger.info(f"Before include request: {app.state.app_request}")


async def after_include_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1

    logger.info(f"After include request: {app.state.app_request}")


async def before_app_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request = 1
    logger.info(f"Before app request: {app.state.app_request}")


async def after_app_request(scope, receive, send):
    app = scope["app"]
    app.state.app_request += 1

    logger.info(f"After app request: {app.state.app_request}")


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
                        before_request=[before_path_request],
                        after_request=[after_path_request],
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
