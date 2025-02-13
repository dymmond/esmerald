from esmerald import Esmerald, Gateway, Include
from lilya.types import Scope, Receive, Send


def before_path_request(scope: Scope, receive: Receive, send: Send):
    # Add logging on entering the request
    ...


def after_path_request(scope: Scope, receive: Receive, send: Send):
    # Add logging on exiting the request
    ...


async def home() -> str:
    return "Hello, World!"


app = Esmerald(
    routes=[
        Gateway(
            "/",
            handler=home,
            before_request=[before_path_request],
            after_request=[after_path_request],
        ),
    ]
)
