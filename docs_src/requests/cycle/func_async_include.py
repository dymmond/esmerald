from esmerald import Esmerald, Gateway, Include
from lilya.types import Scope, Receive, Send


async def before_path_request(scope: Scope, receive: Receive, send: Send):
    # Add logging on entering the request
    ...


async def after_path_request(scope: Scope, receive: Receive, send: Send):
    # Add logging on exiting the request
    ...


async def before_include_request(scope: Scope, receive: Receive, send: Send):
    # Add logging on entering the include
    ...


async def after_include_request(scope: Scope, receive: Receive, send: Send):
    # Add logging on exiting the include
    ...


async def home() -> str:
    return "Hello, World!"


app = Esmerald(
    routes=[
        Include(
            "/",
            before_request=[before_include_request],
            after_request=[after_include_request],
            routes=[
                Gateway(
                    "/",
                    handler=home,
                    before_request=[before_path_request],
                    after_request=[after_path_request],
                ),
            ],
        ),
    ]
)
