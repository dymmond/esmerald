from lilya.types import Receive, Scope, Send
from loguru import logger
from pydantic import BaseModel

from esmerald import ChildEsmerald, Gateway, Include, JSONResponse, Request, post
from esmerald.exceptions import NotAuthorized
from esmerald.interceptors.interceptor import EsmeraldInterceptor
from esmerald.params import Cookie
from esmerald.testclient import create_client


class ErrorInterceptor(EsmeraldInterceptor):
    """"""


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
            raise NotAuthorized() from None


class LoggingInterceptor(EsmeraldInterceptor):
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        logger.info("Intercepted for logging")


class DummyInterceptor:
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        request = Request(scope=scope, receive=receive, send=send)
        request.path_params["name"] = "intercept"


class Item(BaseModel):
    name: str
    sku: str


@post("/create/{name}")
async def create(payload: Item, name: str) -> JSONResponse:
    return JSONResponse({"name": name})


@post("/cookie/{name}")
async def cookie_test(
    payload: Item, name: str, cookie: str = Cookie(value="csrftoken")
) -> JSONResponse:
    """ """


@post("/logging/{name}")
async def logging_view(payload: Item, name: str) -> JSONResponse:
    return JSONResponse({"name": name})


@post("/error")
async def error() -> None:
    """"""


def test_issubclassing_EsmeraldInterceptor(test_client_factory):
    assert issubclass(TestInterceptor, EsmeraldInterceptor)


def test_interceptor_not_implemented(test_client_factory):
    with create_client(routes=[Gateway(handler=error)], interceptors=[ErrorInterceptor]) as client:
        response = client.get("/error")

        assert response.status_code == 500


def test_interceptor_on_application_instance(test_client_factory):
    payload = {"name": "test", "sku": "12345"}

    with create_client(routes=[Gateway(handler=create)], interceptors=[TestInterceptor]) as client:
        response = client.post("/create/test", json=payload)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_application_with_dummy_interceptor(test_client_factory):
    payload = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[Gateway(handler=create)], interceptors=[DummyInterceptor]
    ) as client:
        response = client.post("/create/test", json=payload)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_gateway_level(test_client_factory):
    payload = {"name": "test", "sku": "12345"}

    with create_client(routes=[Gateway(handler=create, interceptors=[TestInterceptor])]) as client:
        response = client.post("/create/test", json=payload)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_include_level(test_client_factory):
    payload = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[Include(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])]
    ) as client:
        response = client.post("/create/test", json=payload)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_nested_include(test_client_factory):
    payload = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[
            Include(
                routes=[Include(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])]
            )
        ]
    ) as client:
        response = client.post("/create/test", json=payload)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald(test_client_factory):
    payload = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/test", json=payload)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald_gateway(test_client_factory):
    payload = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(routes=[Gateway(handler=create, interceptors=[TestInterceptor])])

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/test", json=payload)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald_include(test_client_factory):
    payload = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(
        routes=[Include(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])]
    )

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/test", json=payload)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald_nested_include(test_client_factory):
    payload = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(
        routes=[
            Include(
                routes=[Include(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])]
            )
        ]
    )

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/test", json=payload)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_multiple_interceptors(test_client_factory):
    """
    Uses multiple interceptors and raises a 401 in the CookieInterceptor
    """
    payload = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[Gateway(handler=cookie_test, interceptors=[CookieInterceptor])],
        interceptors=[TestInterceptor],
    ) as client:
        response = client.post("/cookie/test", json=payload, cookies={"csrftoken": "test-cookie"})

        assert response.status_code == 401


def test_multiple_interceptors_change(test_client_factory):
    """
    Uses multiple interceptors and raises a 401 in the CookieInterceptor
    """
    payload = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[Gateway(handler=cookie_test, interceptors=[TestInterceptor])],
        interceptors=[CookieInterceptor],
    ) as client:
        response = client.post("/cookie/test", json=payload, cookies={"csrftoken": "test-cookie"})

        assert response.status_code == 401


def test_multiple_interceptors_change_two(test_client_factory):
    """
    Uses multiple interceptors and raises a 401 in the CookieInterceptor
    """
    payload = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[Gateway(handler=logging_view, interceptors=[TestInterceptor])],
        interceptors=[LoggingInterceptor],
    ) as client:
        response = client.post("/logging/test", json=payload)

        assert response.status_code == 201


def test_interceptor_is_cross_child_and_application(test_client_factory):
    payload = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(routes=[Include(routes=[Include(routes=[Gateway(handler=create)])])])

    with create_client(
        routes=[Include("/child", app=child)], interceptors=[TestInterceptor]
    ) as client:
        response = client.post("/child/create/test", json=payload)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}
