from esmerald import Esmerald, Request, Gateway, Include
from esmerald.exceptions import PermissionDenied
from lilya.protocols.permissions import PermissionProtocol
from lilya.types import ASGIApp, Receive, Scope, Send


class AllowAccess(PermissionProtocol):
    def __init__(self, app: ASGIApp, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope=scope, receive=receive, send=send)

        if "allow-access" in request.headers:
            await self.app(scope, receive, send)
            return
        raise PermissionDenied()


class AdminAccess(PermissionProtocol):
    def __init__(self, app: ASGIApp, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        request = Request(scope=scope, receive=receive, send=send)

        if "allow-admin" in request.headers:
            await self.app(scope, receive, send)
            return
        raise PermissionDenied()


@get()
async def home():
    return "Hello world"


@get()
async def user(user: str):
    return f"Hello {user}"


# Via Path
app = Esmerald(
    routes=[
        Gateway("/", handler=home),
        Gateway(
            "/{user}",
            handler=user,
            permissions=[AdminAccess],
        ),
    ],
    permissions=[AllowAccess],
)


# Via Include
app = Esmerald(
    routes=[
        Include(
            "/",
            routes=[
                Gateway("/", handler=home),
                Gateway(
                    "/{user}",
                    handler=user,
                    permissions=[AdminAccess],
                ),
            ],
            permissions=[AllowAccess],
        )
    ]
)
