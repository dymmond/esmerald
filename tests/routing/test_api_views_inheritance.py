from esmerald import APIView, SimpleAPIView, get
from esmerald.permissions import DenyAll
from esmerald.testclient import create_client


class MyAPIView(APIView):
    permissions = [DenyAll]

    @get("/home")
    async def home(self) -> str:
        return "home"


class MySimpleAPIView(SimpleAPIView):
    @get()
    async def get(self) -> str:
        return "home simple"


def test_cannot_access_apiview(test_client_factory):
    with create_client(routes=[MyAPIView]) as client:
        response = client.get("/home")
        assert response.status_code == 403
