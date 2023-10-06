import pytest

import esmerald
from esmerald import APIView, Gateway, ImproperlyConfigured, SimpleAPIView, get
from esmerald.testclient import create_client


class MyAPIView(APIView):
    @get()
    async def home(self) -> str:
        return "home"


class MySimpleAPIView(SimpleAPIView):
    @get()
    async def get(self) -> str:
        return "home simple"


@pytest.mark.parametrize(
    "handler,return_message", [(MyAPIView, "home"), (MySimpleAPIView, "home simple")]
)
def test_can_access_apiview(test_client_factory, handler, return_message):
    with create_client(routes=[Gateway(handler=handler)]) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == return_message


@pytest.mark.parametrize("method", list(SimpleAPIView.http_allowed_methods))
def test_raises_improperly_configured_on_wrong_method_in_simple_api(method):
    handler = getattr(esmerald, method)
    with pytest.raises(ImproperlyConfigured):

        class MySimpleAPIView(SimpleAPIView):
            @handler()
            async def values(self) -> str:
                return "home simple"
