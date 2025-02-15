from esmerald import APIView, get
from esmerald.permissions import AllowAny, DenyAll, IsAuthenticated
from esmerald.testclient import create_client


class MyAPIView(APIView):
    permissions = [DenyAll]

    @get("/home")
    async def home(self) -> str:
        return "home"


class MySimpleAPIView(MyAPIView):
    permissions = [AllowAny]

    @get(
        "/new-home",
    )
    async def get(self) -> str:
        return "home simple"


class AnotherAPI(MyAPIView):
    permissions = [AllowAny]

    @get("/another", permissions=[IsAuthenticated])
    async def get(self) -> str: ...


def test_cannot_access_apiview(test_client_factory):
    with create_client(routes=[MyAPIView]) as client:
        response = client.get("/home")

        assert response.status_code == 403
        assert MyAPIView.permissions == [DenyAll]


def test_cannot_access_simple_apiview(test_client_factory):
    with create_client(routes=[MySimpleAPIView]) as client:
        response = client.get("/new-home")

        assert response.status_code == 403
        assert MySimpleAPIView.permissions == [DenyAll, AllowAny]


def test_inheritance_total(test_client_factory):
    with create_client(routes=[AnotherAPI], enable_openapi=False) as client:
        response = client.get("/another")

        assert response.status_code == 403
        assert AnotherAPI.permissions == [DenyAll, AllowAny]

        permissions = client.app.routes[0].handler._application_permissions

        assert len(permissions) == 3
