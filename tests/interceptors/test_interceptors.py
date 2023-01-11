from pydantic import BaseModel
from starlette.types import Receive, Scope, Send

from esmerald import ChildEsmerald, Gateway, Include, JSONResponse, Request, post
from esmerald.exceptions import NotAuthorized
from esmerald.interceptors.interceptor import EsmeraldInterceptor
from esmerald.params import Cookie
from esmerald.requests import Request
from esmerald.testclient import create_client


class TestInterceptor(EsmeraldInterceptor):
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        request = Request(scope=scope, receive=receive, send=send)
        request.path_params["name"] = "intercept"


class CookieInterceptor(EsmeraldInterceptor):
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        request = Request(scope=scope, receive=receive, send=send)
        csrf_token = request.cookies["csrftoken"]

        try:
            int(csrf_token)
        except (TypeError, ValueError):
            raise NotAuthorized()


class DummyInterceptor:
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        request = Request(scope=scope, receive=receive, send=send)
        request.path_params["name"] = "intercept"


class Item(BaseModel):
    name: str
    sku: str


@post("/create/{name}")
async def create(data: Item, name: str) -> JSONResponse:
    return JSONResponse({"name": name})


@post("/cookie/{name}")
async def cookie_test(
    data: Item, name: str, cookie: str = Cookie(value="csrftoken")
) -> JSONResponse:
    breakpoint()
    return JSONResponse({"name": name, "cookie": cookie})


def test_issubclassing_EsmeraldInterceptor():
    assert issubclass(TestInterceptor, EsmeraldInterceptor)


def test_interceptor_on_application_instance():
    data = {"name": "test", "sku": "12345"}

    with create_client(routes=[Gateway(handler=create)], interceptors=[TestInterceptor]) as client:
        response = client.post("/create/test", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_application_with_dummy_interceptor():
    data = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[Gateway(handler=create)], interceptors=[DummyInterceptor]
    ) as client:
        response = client.post("/create/test", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_gateway_level():
    data = {"name": "test", "sku": "12345"}

    with create_client(routes=[Gateway(handler=create, interceptors=[TestInterceptor])]) as client:
        response = client.post("/create/test", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_include_level():
    data = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[Include(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])]
    ) as client:
        response = client.post("/create/test", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_nested_include():
    data = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[
            Include(
                routes=[Include(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])]
            )
        ]
    ) as client:
        response = client.post("/create/test", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald():
    data = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/test", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald_gateway():
    data = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(routes=[Gateway(handler=create, interceptors=[TestInterceptor])])

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/test", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald_include():
    data = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(
        routes=[Include(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])]
    )

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/test", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald_nested_include():
    data = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(
        routes=[
            Include(
                routes=[Include(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])]
            )
        ]
    )

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/test", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_multiple_interceptors():
    """
    Uses multiple interceptors and raises a 401 in the CookieInterceptor
    """
    data = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[Gateway(handler=cookie_test, interceptors=[CookieInterceptor])],
        interceptors=[TestInterceptor],
    ) as client:
        response = client.post("/cookie/test", json=data, cookies={"csrftoken": "test-cookie"})

        assert response.status_code == 401
