import pytest

import esmerald
from esmerald import (
    APIView,
    Gateway,
    ImproperlyConfigured,
    SimpleAPIView,
    delete,
    get,
    patch,
    post,
    put,
)
from esmerald.routing.apis.generics import CreateAPIView, DeleteAPIView, ReadAPIView
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
def test_raises_improperly_configured_on_wrong_method_in_simple_api(test_client_factory, method):
    handler = getattr(esmerald, method)
    with pytest.raises(ImproperlyConfigured):

        class MySimpleAPIView(SimpleAPIView):
            @handler()
            async def values(self) -> str:
                return "home simple"


@pytest.mark.parametrize("value", list(CreateAPIView.http_allowed_methods))
def test_create_api_view(test_client_factory, value):
    handler = getattr(esmerald, value)

    class MyCreateAPIView(CreateAPIView):
        @post()
        async def post(self) -> str:
            return f"home {value}"

        @put()
        async def put(self) -> str:
            return f"home {value}"

        @patch()
        async def patch(self) -> str:
            return f"home {value}"

    with create_client(routes=[Gateway(handler=MyCreateAPIView)]) as client:
        response = getattr(client, value)("/")
        assert response.status_code == handler().status_code
        assert response.json() == f"home {value}"


@pytest.mark.parametrize("value", list(ReadAPIView.http_allowed_methods))
def test_read_api_view(test_client_factory, value):
    handler = getattr(esmerald, value)

    class MyReadAPIView(ReadAPIView):
        @get()
        async def get(self) -> str:
            return f"home {value}"

    with create_client(routes=[Gateway(handler=MyReadAPIView)]) as client:
        response = getattr(client, value)("/")
        assert response.status_code == handler().status_code
        assert response.json() == f"home {value}"


@pytest.mark.parametrize("value", list(DeleteAPIView.http_allowed_methods))
def test_delete_api_view(test_client_factory, value):
    handler = getattr(esmerald, value)

    class MyDeleteAPIView(DeleteAPIView):
        @delete()
        async def delete(self) -> None:
            ...  # pragma: no cover

    with create_client(routes=[Gateway(handler=MyDeleteAPIView)]) as client:
        response = getattr(client, value)("/")
        assert response.status_code == handler().status_code


@pytest.mark.parametrize(
    "value",
    list(CreateAPIView.http_allowed_methods)
    + list(ReadAPIView.http_allowed_methods)
    + list(DeleteAPIView.http_allowed_methods),
)
def test_all_api_view(test_client_factory, value):
    handler = getattr(esmerald, value)

    class GenericAPIView(CreateAPIView, ReadAPIView, DeleteAPIView):
        @post()
        async def post(self) -> str:
            return f"home {value}"

        @put()
        async def put(self) -> str:
            return f"home {value}"

        @patch()
        async def patch(self) -> str:
            return f"home {value}"

        @delete()
        async def delete(self) -> None:
            ...  # pragma: no cover

        @get()
        async def get(self) -> str:
            return f"home {value}"

    with create_client(routes=[Gateway(handler=GenericAPIView)]) as client:
        response = getattr(client, value)("/")
        assert response.status_code == handler().status_code
