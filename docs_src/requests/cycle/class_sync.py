from ravyn import Ravyn, Gateway, Include
from lilya.types import Scope, Receive, Send


class BeforePathRequest:
    def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Add logging on entering the request
        ...


class AfterPathRequest:
    def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Add logging on exiting the request
        ...


async def home() -> str:
    return "Hello, World!"


app = Ravyn(
    routes=[
        Gateway(
            "/",
            handler=home,
            before_request=[BeforePathRequest],
            after_request=[AfterPathRequest],
        ),
    ]
)
