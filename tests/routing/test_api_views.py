from typing import Any, Dict, List, Mapping, Sequence, Set

import pytest
from pydantic import BaseModel

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
from esmerald.routing.apis.generics import CreateAPIView, DeleteAPIView, ListAPIView, ReadAPIView
from esmerald.testclient import create_client


class TestModel(BaseModel):
    name: str


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


@pytest.mark.parametrize("value,method", [("create_user", "post"), ("read_item", "get")])
def test_all_api_view_custom(test_client_factory, value, method):
    class GenericAPIView(CreateAPIView, ReadAPIView, DeleteAPIView):
        extra_allowed: List[str] = ["create_user", "read_item"]

        @post(status_code=200)
        async def create_user(self) -> str:
            return f"home {value}"

        @get()
        async def read_item(self) -> str:
            return f"home {value}"

    with create_client(routes=[Gateway(handler=GenericAPIView)]) as client:
        response = getattr(client, method)("/")
        assert response.status_code == 200
        assert response.json() == f"home {value}"


@pytest.mark.parametrize(
    "value",
    [("create_user",), {"create_user"}, {"name": "create_user"}],
    ids=["tuple", "set", "dict"],
)
def test_all_api_view_custom_error(test_client_factory, value):
    with pytest.raises(AssertionError):

        class GenericAPIView(CreateAPIView, ReadAPIView, DeleteAPIView):
            extra_allowed: List[str] = ("create_user", "read_item")


@pytest.mark.parametrize(
    "value", [value for value in SimpleAPIView.http_allowed_methods if value != "get"]
)
def test_default_parameters_raise_error_on_wrong_handler(test_client_factory, value):
    handler = getattr(esmerald, value)

    with pytest.raises(ImproperlyConfigured) as raised:

        class GenericAPIView(CreateAPIView, ReadAPIView, DeleteAPIView):
            extra_allowed: List[str] = ["create_user"]

            @handler("/")
            def get(self) -> None:
                ...

            @handler("/")
            def create_user() -> None:
                ...

    assert (
        raised.value.detail
        == f"The function 'get' must implement the 'get()' handler, got '{value}()' instead."
    )


def test_list_api_view(test_client_factory):
    class GenericAPIView(ListAPIView):
        @get()
        def get(self) -> List[str]:
            return ["home", "list"]

    with create_client(routes=[Gateway(handler=GenericAPIView)]) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert len(response.json()) == 2


@pytest.mark.parametrize(
    "return_type",
    [
        str,
        dict,
        set,
        int,
        float,
        Dict[str, str],
        Set[int],
        Mapping[str, Any],
        Sequence[str],
        Sequence[int],
        Sequence[float],
        Sequence[TestModel],
    ],
)
def test_raises_improperly_configured_on_non_list_types(test_client_factory, return_type):
    with pytest.raises(ImproperlyConfigured):

        class GenericAPIView(ListAPIView):
            @get()
            def get(self) -> return_type:
                ...


@pytest.mark.parametrize(
    "return_type,method",
    [
        (List[str], "get"),
        (List[int], "put"),
        (List[float], "patch"),
        (List[TestModel], "post"),
    ],
)
def test_list_api_view_works_for_many(test_client_factory, return_type, method):
    handler = getattr(esmerald, method)

    class GenericListAPIView(ListAPIView):
        extra_allowed = ["return_list"]

        @handler()
        def return_list(self) -> return_type:
            return ["home", "list"]

    with create_client(routes=[Gateway(handler=GenericListAPIView)]) as client:
        response = getattr(client, method)("/")
        assert response.status_code == handler().status_code
        assert len(response.json()) == 2
