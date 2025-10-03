from ravyn import Ravyn, Gateway, Include
from lilya.types import Scope, Receive, Send


async def before_path_request(scope: Scope, receive: Receive, send: Send):
    # Add logging on entering the request
    ...


async def after_path_request(scope: Scope, receive: Receive, send: Send):
    # Add logging on exiting the request
    ...


async def home() -> str:
    return "Hello, World!"


app = Ravyn(
    routes=[
        Gateway(
            "/",
            handler=home,
            before_request=[before_path_request],
            after_request=[after_path_request],
        ),
    ]
)
