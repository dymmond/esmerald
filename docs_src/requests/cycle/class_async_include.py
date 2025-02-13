from esmerald import Esmerald, Gateway, Include
from lilya.types import Scope, Receive, Send


class BeforePathRequest:
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Add logging on entering the request
        ...


class AfterPathRequest:
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Add logging on exiting the request
        ...


class BeforeIncludeRequest:
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Add logging on entering the include
        ...


class AfterIncludeRequest:
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        # Add logging on exiting the include
        ...


async def home() -> str:
    return "Hello, World!"


app = Esmerald(
    routes=[
        Include(
            "/",
            before_request=[BeforeIncludeRequest],
            after_request=[AfterIncludeRequest],
            routes=[
                Gateway(
                    "/",
                    handler=home,
                    before_request=[BeforePathRequest],
                    after_request=[AfterPathRequest],
                ),
            ],
        ),
    ]
)
