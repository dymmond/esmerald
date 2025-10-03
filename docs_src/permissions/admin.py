from ravyn import APIView, Ravyn, Gateway, JSONResponse, Request, get
from ravyn.permissions import AllowAny, IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly


class IsAdmin(IsAdminUser):
    def is_user_staff(self, request: "Request") -> bool:
        """
        Add logic to verify if a user is staff
        """


class IsUserAuthenticated(IsAuthenticated):
    def is_user_authenticated(self, request: "Request") -> bool:
        """
        Add logic to verify if a user is staff
        """


class IsAuthOrReadOnly(IsAuthenticatedOrReadOnly):
    def is_user_authenticated(self, request: "Request") -> bool:
        """
        Add logic to verify if a user is staff
        """


@get()
async def home() -> None: ...


class UserAPIView(APIView):
    path = "/users"
    permissions = [IsUserAuthenticated]

    @get("/admin", permissions=[IsAdmin])
    async def admin(self, request: Request) -> JSONResponse:
        return JSONResponse({"message": "ok"})


app = Ravyn(
    routes=[Gateway("/home", handler=home), Gateway(handler=UserAPIView)],
    permissions=[AllowAny],
)
