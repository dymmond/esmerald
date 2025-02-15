from esmerald import APIView, get
from esmerald.permissions import AllowAny, DenyAll
from esmerald.testclient import create_client


class MyAPIView(APIView):
    permissions = [DenyAll]

    @get("/home")
    async def home(self) -> str:
        return "home"


class MySimpleAPIView(MyAPIView):
    permissions = [AllowAny]

    @get("/new-home")
    async def get(self) -> str:
        return "home simple"


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
