from pydantic import BaseModel
from starlette.types import ASGIApp, Receive, Scope, Send

from esmerald import ChildEsmerald, Gateway, Include, JSONResponse, Request, post, put
from esmerald.interceptors.interceptor import EsmeraldInterceptor
from esmerald.testclient import EsmeraldTestClient, create_client


class TestInterceptor(EsmeraldInterceptor):
    async def intercept(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        request = Request(scope=scope, receive=receive, send=send)
        # body = await request.body()
        request.path_params["name"] = "intercept"


class Item(BaseModel):
    name: str
    sku: str


@post("/create/{name}")
async def create(data: Item, name: str) -> JSONResponse:
    return JSONResponse({"name": name})


def test_interceptor_on_application_instance():
    data = {"name": "test", "sku": "12345"}

    with create_client(routes=[Gateway(handler=create)], interceptors=[TestInterceptor]) as client:
        response = client.post("/create/coise", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_gateway_level():
    data = {"name": "test", "sku": "12345"}

    with create_client(routes=[Gateway(handler=create, interceptors=[TestInterceptor])]) as client:
        response = client.post("/create/coise", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_include_level():
    data = {"name": "test", "sku": "12345"}

    with create_client(
        routes=[Include(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])]
    ) as client:
        response = client.post("/create/coise", json=data)

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
        response = client.post("/create/coise", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald():
    data = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/coise", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald_gateway():
    data = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(routes=[Gateway(handler=create, interceptors=[TestInterceptor])])

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/coise", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


def test_interceptor_on_child_esmerald_include():
    data = {"name": "test", "sku": "12345"}

    child = ChildEsmerald(
        routes=[Include(routes=[Gateway(handler=create)], interceptors=[TestInterceptor])]
    )

    with create_client(routes=[Include("/child", app=child)]) as client:
        response = client.post("/child/create/coise", json=data)

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
        response = client.post("/child/create/coise", json=data)

        assert response.status_code == 201
        assert response.json() == {"name": "intercept"}


# def test_interceptor_on_child_esmerald_from_top_application():
#     data = {"name": "test", "sku": "12345"}

#     child = ChildEsmerald(routes=[Include(routes=[Include(routes=[Gateway(handler=create)])])])

#     with create_client(
#         routes=[Include("/child", app=child)], interceptors=[TestInterceptor]
#     ) as client:
#         response = client.post("/child/create/coise", json=data)

#         assert response.status_code == 201
#         assert response.json() == {"name": "intercept"}
