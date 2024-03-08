from pydantic import BaseModel, EmailStr

from esmerald import (
    APIView,
    ChildEsmerald,
    Esmerald,
    Gateway,
    Include,
    Request,
    WebSocket,
    WebSocketGateway,
    get,
    post,
    settings,
    websocket,
)
from esmerald.config.jwt import JWTConfig
from esmerald.contrib.auth.saffier.base_user import User
from esmerald.exceptions import NotAuthorized
from esmerald.middleware.authentication import AuthResult, BaseAuthMiddleware
from esmerald.permissions import IsAdminUser
from esmerald.security.jwt.token import Token
from lilya._internal._connection import Connection
from lilya.middleware import DefineMiddleware as LilyaMiddleware
from lilya.types import ASGIApp
from saffier.exceptions import ObjectNotFound


class JWTAuthMiddleware(BaseAuthMiddleware):
    def __init__(self, app: "ASGIApp", config: "JWTConfig"):
        super().__init__(app)
        self.app = app
        self.config = config

    async def retrieve_user(self, user_id) -> User:
        try:
            return await User.get(pk=user_id)
        except ObjectNotFound:
            raise NotAuthorized()

    async def authenticate(self, request: Connection) -> AuthResult:
        token = request.headers.get(self.config.api_key_header)

        if not token:
            raise NotAuthorized("JWT token not found.")

        token = Token.decode(
            token=token, key=self.config.signing_key, algorithm=self.config.algorithm
        )

        user = await self.retrieve_user(token.sub)
        return AuthResult(user=user)


class IsAdmin(IsAdminUser):
    def is_user_staff(self, request: "Request") -> bool:
        """
        Add logic to verify if a user is staff
        """


@get()
async def home() -> None: ...


@get("/me")
async def me(request: Request) -> str:
    return "Hello, world!"


@websocket(path="/ws")
async def websocket_endpoint_include(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, new world!")
    await socket.close()


class User(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserApiView(APIView):
    path = "/users"

    @post("/create")
    async def create_user(self, data: User, request: Request) -> None: ...

    @websocket(path="/ws")
    async def websocket_endpoint(self, socket: WebSocket) -> None:
        await socket.accept()
        await socket.send_text("Hello, world!")
        await socket.close()


child_esmerald = ChildEsmerald(
    routes=[Gateway("/home", handler=home), Gateway(handler=UserApiView)]
)

jwt_config = JWTConfig(
    signing_key=settings.secret_key_key_key,
)


app = Esmerald(
    routes=[
        Include(
            "/",
            routes=[
                Gateway(handler=me),
                WebSocketGateway(handler=websocket_endpoint_include),
                Include("/admin", child_esmerald),
            ],
        )
    ],
    permissions=[IsAdmin],
    middleware=[LilyaMiddleware(JWTAuthMiddleware, config=jwt_config)],
)
