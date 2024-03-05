import contextlib
import uuid
from dataclasses import dataclass

import pytest
from pydantic.dataclasses import dataclass as pydantic_dataclass
from starlette.responses import JSONResponse, PlainTextResponse, Response as StarletteResponse
from starlette.routing import Host, NoMatchFound
from starlette.websockets import WebSocket, WebSocketDisconnect

from esmerald.applications import Esmerald
from esmerald.enums import MediaType
from esmerald.permissions import AllowAny, DenyAll
from esmerald.requests import Request
from esmerald.responses import Response
from esmerald.responses.encoders import UJSONResponse
from esmerald.routing.apis.views import APIView
from esmerald.routing.gateways import Gateway, WebSocketGateway
from esmerald.routing.handlers import get, post, put, websocket
from esmerald.routing.router import Include, Router
from esmerald.testclient import create_client


@get(path="/", permissions=[DenyAll])
async def deny_access(request: Request) -> JSONResponse:
    """ """


@get(path="/", permissions=[AllowAny])
async def allow_access(request: Request) -> JSONResponse:
    return JSONResponse("Hello, world")


@get(path="/", media_type=MediaType.TEXT, status_code=200)
async def homepage(request: Request) -> StarletteResponse:
    return StarletteResponse("Hello, world")


@get(path="/", media_type=MediaType.TEXT, status_code=200)
async def users(request: Request) -> StarletteResponse:
    return StarletteResponse("All users")


@get(path="/", media_type=MediaType.TEXT, status_code=200)
async def user(request: Request, username: str) -> StarletteResponse:
    content = "User " + username
    return StarletteResponse(content)


@get(path="/me", media_type=MediaType.TEXT, status_code=200)
async def user_me(request: Request) -> StarletteResponse:
    content = "User fixed me"
    return StarletteResponse(content)


@put(path="/", media_type=MediaType.TEXT, status_code=200)
async def disable_user(request: Request) -> StarletteResponse:
    content = "User " + request.path_params["username"] + " disabled"
    return StarletteResponse(content)


@get(path="/", media_type=MediaType.TEXT, status_code=200)
async def user_no_match(request: Request) -> StarletteResponse:  # pragma: no cover
    content = "User fixed no match"
    return StarletteResponse(content)


@get(path="/", media_type=MediaType.TEXT, status_code=200)
async def func_homepage(request: Request) -> StarletteResponse:
    return StarletteResponse("Hello, world!")


@post(path="/", media_type=MediaType.TEXT, status_code=200)
async def contact(request: Request) -> StarletteResponse:
    return StarletteResponse("Hello, POST!")


@get(path="/", status_code=200)
async def int_convertor(request: Request) -> None:
    number = request.path_params["param"]
    return UJSONResponse({"int": number})


@get(path="/", status_code=200)
async def float_convertor(request: Request) -> None:
    num = request.path_params["param"]
    return JSONResponse({"float": num})


@get(path="/", status_code=200)
async def path_convertor(request: Request) -> None:
    path = request.path_params["param"]
    return UJSONResponse({"path": path})


@get(path="/", status_code=200)
async def uuid_converter(request: Request) -> None:
    uuid_param = request.path_params["param"]
    return UJSONResponse({"uuid": str(uuid_param)})


@get(path="/", status_code=200)
async def path_with_parentheses(request: Request) -> None:
    number = request.path_params["param"]
    return UJSONResponse({"int": number})


@websocket(path="/")
async def websocket_endpoint(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, world!")
    await socket.close()


@websocket(path="/")
async def websocket_params(socket: WebSocket, room: str) -> None:
    await socket.accept()
    await socket.send_text(f"Hello, {room}!")
    await socket.close()


@websocket(path="/")
async def websocket_params_chat(socket: WebSocket, chat: str) -> None:
    await socket.accept()
    await socket.send_text(f"Hello, {chat}!")
    await socket.close()


@websocket(path="/")
async def websocket_endpoint_include(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, new world!")
    await socket.close()


class MyAPIView(APIView):
    path = "test"

    @get(path="/")
    async def esmerald(self) -> UJSONResponse:
        return UJSONResponse({"myapiview": "fluid"})

    @get(path="/name/{name}")
    async def name(self, name: str) -> UJSONResponse:
        return UJSONResponse({"myapiview": name})


class AnotherMyAPIView(APIView):
    path = "test"

    @get(path="/")
    async def esmerald(self, param: str) -> UJSONResponse:
        return UJSONResponse({"myapiview": param})

    @get(path="/name/{name}")
    async def name(self, param: str, name: str) -> UJSONResponse:
        return UJSONResponse({"myapiview": name, "param": param})


class TestMyAPIView(APIView):
    __test__ = False
    path = "fluid/{name}"

    @get(path="/")
    async def esmerald(self, param: str, name: str) -> UJSONResponse:
        return UJSONResponse({"param": param, "name": name})

    @get(path="/name/{endpoint}")
    async def name(self, param: str, name: str, endpoint: str) -> UJSONResponse:
        return UJSONResponse({"param": param, "name": name, "endpoint": endpoint})

    @websocket(path="/socket")
    async def websocket_endpoint_include(self, socket: WebSocket, param: str, name: str) -> None:
        await socket.accept()
        await socket.send_text("Hello new world!")
        await socket.close()


routes = [
    Gateway("/", handler=homepage, name="homepage"),
    Gateway("/apiview", handler=MyAPIView, name="testapiview"),
    Include("/apinested", routes=[Gateway("/api", handler=MyAPIView)]),
    Include(
        "/apinest",
        routes=[
            Include("/apinested", routes=[Gateway("/api", handler=MyAPIView)]),
            Include("/apiparam/", routes=[Gateway("/api/{param}", handler=AnotherMyAPIView)]),
        ],
    ),
    Include(
        "/nested",
        routes=[
            Include(
                path="/test/",
                routes=[Gateway(path="/", handler=homepage, name="nested")],
            ),
            Include(
                path="/another",
                routes=[
                    Include(
                        path="/test",
                        routes=[Gateway(path="/{param}", handler=homepage, name="nested")],
                    )
                ],
            ),
        ],
    ),
    Include(
        path="/test",
        routes=[
            Include(
                path="/my",
                routes=[
                    Include(
                        path="/api",
                        routes=[
                            Include(
                                path="/view",
                                routes=[Gateway(path="/here/{param}", handler=TestMyAPIView)],
                            )
                        ],
                    )
                ],
            )
        ],
    ),
    Include(
        "/users",
        routes=[
            Gateway("/", handler=users),
            Gateway("/personal", handler=user_me),
            Gateway("/{username}", handler=user, name="user"),
            Gateway("/{username}:disable", handler=disable_user),
            Gateway("/nomatch", handler=user_no_match),
        ],
    ),
    Include(
        "/static",
        app=StarletteResponse("xxxxx", media_type=MediaType.PNG, status_code=200),
    ),
    Gateway("/func", handler=func_homepage),
    Gateway("/func", handler=contact),
    Gateway("/int/{param:int}", handler=int_convertor, name="int-convertor"),
    Gateway("/float/{param:float}", handler=float_convertor, name="float-convertor"),
    Gateway("/path/{param:path}", handler=path_convertor, name="path-convertor"),
    Gateway("/uuid/{param:uuid}", handler=uuid_converter, name="uuid-convertor"),
    # Gateway with chars that conflict with regex meta chars
    Gateway(
        "/path-with-parentheses({param:int})",
        handler=path_with_parentheses,
        name="path-with-parentheses",
    ),
    WebSocketGateway("/ws", handler=websocket_endpoint, name="websocket_endpoint"),
    WebSocketGateway("/ws/{room}", handler=websocket_params, name="ws-room"),
    Include(
        "/websockets",
        routes=[
            WebSocketGateway("/wsocket", handler=websocket_endpoint_include, name="wsocket"),
            WebSocketGateway("/wsocket/{chat}", handler=websocket_params_chat, name="ws-chat"),
        ],
    ),
    Gateway("/deny", handler=deny_access, name="deny_access"),
    Gateway("/allow", handler=allow_access, name="allow_access"),
]


@pytest.mark.filterwarnings(
    r"ignore"
    r":Trying to detect encoding from a tiny portion of \(5\) byte\(s\)\."
    r":UserWarning"
    r":charset_normalizer.api"
)
def test_router(test_client_factory):
    with create_client(routes=routes) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "Hello, world"

        response = client.post("/")
        assert response.status_code == 405
        assert response.json()["detail"] == "Method POST not allowed."
        assert response.headers["content-type"] == MediaType.JSON

        response = client.get("/foo")
        assert response.status_code == 404
        assert response.json()["detail"] == "The resource cannot be found."

        response = client.get("/users")
        assert response.status_code == 200
        assert response.text == "All users"

        response = client.get("/users/esmerald")
        assert response.status_code == 200
        assert response.text == "User esmerald"

        response = client.get("/users/personal/me")
        assert response.status_code == 200
        assert response.text == "User fixed me"

        response = client.get("/users/esmerald/")
        assert response.status_code == 200
        assert response.url == "http://testserver/users/esmerald"
        assert response.text == "User esmerald"

        response = client.put("/users/esmerald:disable")
        assert response.status_code == 200
        assert response.url == "http://testserver/users/esmerald:disable"
        assert response.text == "User esmerald disabled"

        response = client.get("/users/nomatch")
        assert response.status_code == 200
        assert response.text == "User nomatch"

        response = client.get("/static/123")
        assert response.status_code == 200
        assert response.text == "xxxxx"

        response = client.get("/nested/test")
        assert response.status_code == 200
        assert response.text == "Hello, world"

        response = client.get("/nested/another/test/fluid")
        assert response.status_code == 200
        assert response.text == "Hello, world"


@pytest.mark.filterwarnings(
    r"ignore"
    r":Trying to detect encoding from a tiny portion of \(5\) byte\(s\)\."
    r":UserWarning"
    r":charset_normalizer.api"
)
def test_router_permissions(test_client_factory):
    with create_client(routes=routes) as client:
        response = client.get("/deny")
        assert response.status_code == 403
        assert response.json()["detail"] == "You do not have permission to perform this action."

        response = client.get("/allow")
        assert response.status_code == 200
        assert response.json() == "Hello, world"


@pytest.mark.filterwarnings(
    r"ignore"
    r":Trying to detect encoding from a tiny portion of \(5\) byte\(s\)\."
    r":UserWarning"
    r":charset_normalizer.api"
)
def test_router_apiview(test_client_factory):
    with create_client(routes=routes) as client:
        response = client.get("/apiview/test")
        assert response.status_code == 200
        assert response.json() == {"myapiview": "fluid"}

        response = client.get("/apinested/api/test")
        assert response.status_code == 200
        assert response.json() == {"myapiview": "fluid"}

        response = client.get("/apinest/apinested/api/test")
        assert response.status_code == 200
        assert response.json() == {"myapiview": "fluid"}

        response = client.get("/apinest/apinested/api/test/name/esmerald")
        assert response.status_code == 200
        assert response.json() == {"myapiview": "esmerald"}

        response = client.get("/apinest/apiparam/api/fluid/test")
        assert response.status_code == 200
        assert response.json() == {"myapiview": "fluid"}

        response = client.get("/apinest/apiparam/api/fluid/test/name/esmerald")
        assert response.status_code == 200
        assert response.json() == {"myapiview": "esmerald", "param": "fluid"}

        response = client.get("/test/my/api/view/here/param/fluid/test")
        assert response.status_code == 200
        assert response.json() == {"name": "test", "param": "param"}

        response = client.get("/test/my/api/view/here/param/fluid/test/name/endpot")
        assert response.status_code == 200
        assert response.json() == {
            "name": "test",
            "param": "param",
            "endpoint": "endpot",
        }


@pytest.mark.filterwarnings(
    r"ignore"
    r":Trying to detect encoding from a tiny portion of \(5\) byte\(s\)\."
    r":UserWarning"
    r":charset_normalizer.api"
)
def test_router_apiview_with_websockets(test_client_factory):
    with create_client(routes=routes) as client:
        with client.websocket_connect("/test/my/api/view/here/param/fluid/test/socket") as ws:
            data = ws.receive_text()
            assert data
            assert data == "Hello new world!"


def test_router_add_websocket_route_one(test_client_factory):
    with create_client(routes=routes) as client:
        with client.websocket_connect("/ws") as session:
            text = session.receive_text()
            assert text == "Hello, world!"

        with client.websocket_connect("/ws/test") as session:
            text = session.receive_text()
            assert text == "Hello, test!"

        with client.websocket_connect("/websockets/wsocket") as session:
            text = session.receive_text()
            assert text == "Hello, new world!"

        with client.websocket_connect("/websockets/wsocket/test") as session:
            text = session.receive_text()
            assert text == "Hello, test!"


def test_route_converters(test_client_factory):
    # Test integer conversion
    with create_client(routes=routes) as client:
        app = client.app

        response = client.get("/int/5")
        assert response.status_code == 200
        assert response.json() == {"int": 5}
        assert app.url_path_for("int-convertor", param=5) == "/int/5"

        # Test path with parentheses
        response = client.get("/path-with-parentheses(7)")
        assert response.status_code == 200
        assert response.json() == {"int": 7}
        assert app.url_path_for("path-with-parentheses", param=7) == "/path-with-parentheses(7)"

        # Test float conversion
        response = client.get("/float/25.5")
        assert response.status_code == 200
        assert response.json() == {"float": 25.5}
        assert app.url_path_for("float-convertor", param=25.5) == "/float/25.5"

        # Test path conversion
        response = client.get("/path/some/example")
        assert response.status_code == 200
        assert response.json() == {"path": "some/example"}
        assert app.url_path_for("path-convertor", param="some/example") == "/path/some/example"

        # Test UUID conversion
        response = client.get("/uuid/ec38df32-ceda-4cfa-9b4a-1aeb94ad551a")
        assert response.status_code == 200
        assert response.json() == {"uuid": "ec38df32-ceda-4cfa-9b4a-1aeb94ad551a"}
        assert (
            app.url_path_for(
                "uuid-convertor",
                param=uuid.UUID("ec38df32-ceda-4cfa-9b4a-1aeb94ad551a"),
            )
            == "/uuid/ec38df32-ceda-4cfa-9b4a-1aeb94ad551a"
        )


def test_url_path_for(test_client_factory):
    with create_client(routes=routes) as client:
        app = client.app

        assert app.url_path_for("homepage") == "/"
        assert app.url_path_for("user", username="esmerald") == "/users/esmerald"
        assert app.url_path_for("websocket_endpoint") == "/ws"

        with pytest.raises(NoMatchFound, match='No route exists for name "broken" and params "".'):
            assert app.url_path_for("broken")
        with pytest.raises(
            NoMatchFound,
            match='No route exists for name "broken" and params "key, key2".',
        ):
            assert app.url_path_for("broken", key="value", key2="value2")
        with pytest.raises(AssertionError):
            app.url_path_for("user", username="fluid/esmerald")
        with pytest.raises(AssertionError):
            app.url_path_for("user", username="")


def test_url_for(test_client_factory):
    with create_client(routes=routes) as client:
        app = client.app

        assert (
            app.url_path_for("homepage").make_absolute_url(base_url="https://example.org")
            == "https://example.org/"
        )
        assert (
            app.url_path_for("homepage").make_absolute_url(
                base_url="https://example.org/root_path/"
            )
            == "https://example.org/root_path/"
        )
        assert (
            app.url_path_for("user", username="tomchristie").make_absolute_url(
                base_url="https://example.org"
            )
            == "https://example.org/users/tomchristie"
        )
        assert (
            app.url_path_for("user", username="tomchristie").make_absolute_url(
                base_url="https://example.org/root_path/"
            )
            == "https://example.org/root_path/users/tomchristie"
        )
        assert (
            app.url_path_for("websocket_endpoint").make_absolute_url(
                base_url="https://example.org"
            )
            == "wss://example.org/ws"
        )


def test_router_add_route(test_client_factory):
    with create_client(routes=routes) as client:
        response = client.get("/func")
        assert response.status_code == 200
        assert response.text == "Hello, world!"


def test_router_duplicate_path(test_client_factory):
    with create_client(routes=routes) as client:
        response = client.post("/func")
        assert response.status_code == 200
        assert response.text == "Hello, POST!"


def test_router_add_websocket_route(test_client_factory):
    with create_client(routes=routes) as client:
        with client.websocket_connect("/ws") as session:
            text = session.receive_text()
            assert text == "Hello, world!"

    with client.websocket_connect("/ws/test") as session:
        text = session.receive_text()
        assert text == "Hello, test!"


@get(path="/", media_type=MediaType.TEXT)
async def http_endpoint(request: Request) -> Response:
    url = request.url_for("http_endpoint")
    return Response(f"URL: {url}")


@websocket(path="/")
async def websocket_endpoint_switch(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_json({"URL": str(socket.url_for("websocket_endpoint"))})
    await socket.close()


mixed_protocol_app = [
    Gateway(path="/", handler=http_endpoint, name="http_endpoint"),
    WebSocketGateway(path="/", handler=websocket_endpoint_switch, name="websocket_endpoint"),
]


def test_protocol_switch(test_client_factory):
    with create_client(routes=mixed_protocol_app) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.json() == "URL: http://testserver/"

        with client.websocket_connect("/") as session:
            assert session.receive_json() == {"URL": "ws://testserver/"}

        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/404"):
                pass  # pragma: nocover


ok = PlainTextResponse("OK")


@get(path="/")
async def get_ok() -> PlainTextResponse:
    return PlainTextResponse("OK")  # pragma: no cover


def test_include_urls(test_client_factory):
    included = [Include(path="/users", app=ok, name="users")]
    with create_client(routes=included) as client:
        assert client.get("/users").status_code == 200
        assert client.get("/users").url == "http://testserver/users/"
        assert client.get("/users/").status_code == 200
        assert client.get("/users/a").status_code == 200
        assert client.get("/usersa").status_code == 404


def test_reverse_include_urls():
    included = Include("/users", app=ok, name="users")
    assert included.url_path_for("users", path="/a") == "/users/a"

    users = [Gateway("/{username}", handler=get_ok, name="user")]
    included = Include("/{subpath}/users", routes=users, name="users")
    assert included.url_path_for("users:user", subpath="test", username="tom") == "/test/users/tom"
    assert included.url_path_for("users", subpath="test", path="/tom") == "/test/users/tom"


def test_include_at_root(test_client_factory):
    included = [Include("/", app=ok, name="users")]
    with create_client(routes=included) as client:
        assert client.get("/").status_code == 200


@get("/")
async def users_api(request: Request) -> JSONResponse:
    return JSONResponse({"users": [{"username": "tom"}]})


mixed_hosts_app = [
    Host(
        "www.example.org",
        app=Router(
            routes=[
                Gateway("/", handler=homepage, name="homepage"),
                Gateway("/users", handler=users, name="users"),
            ]
        ),
    ),
    Host(
        "api.example.org",
        name="api",
        app=Router(routes=[Gateway("/users", handler=users_api, name="users")]),
    ),
    Host(
        "port.example.org:3600",
        name="port",
        app=Router(routes=[Gateway("/", handler=homepage, name="homepage")]),
    ),
]


def test_host_routing(test_client_factory):
    with create_client(routes=mixed_hosts_app, base_url="https://api.example.org/") as client:
        response = client.get("/users")
        assert response.status_code == 200
        assert response.json() == {"users": [{"username": "tom"}]}

        response = client.get("/")
        assert response.status_code == 404

    with create_client(routes=mixed_hosts_app, base_url="https://www.example.org/") as client:
        response = client.get("/users")
        assert response.status_code == 200
        assert response.text == "All users"

        response = client.get("/")
        assert response.status_code == 200

    with create_client(
        routes=mixed_hosts_app, base_url="https://port.example.org:3600/"
    ) as client:
        response = client.get("/users")
        assert response.status_code == 404

        response = client.get("/")
        assert response.status_code == 200

    with create_client(routes=mixed_hosts_app, base_url="https://port.example.org/") as client:
        response = client.get("/")
        assert response.status_code == 200

    with create_client(
        routes=mixed_hosts_app, base_url="https://port.example.org:5600/"
    ) as client:
        response = client.get("/")
        assert response.status_code == 200


def test_host_reverse_urls(test_client_factory):
    with create_client(routes=mixed_hosts_app) as client:
        app = client.app
        assert (
            app.url_path_for("homepage").make_absolute_url("https://whatever")
            == "https://www.example.org/"
        )
        assert (
            app.url_path_for("users").make_absolute_url("https://whatever")
            == "https://www.example.org/users"
        )
        assert (
            app.url_path_for("api:users").make_absolute_url("https://whatever")
            == "https://api.example.org/users"
        )
        assert (
            app.url_path_for("port:homepage").make_absolute_url("https://whatever")
            == "https://port.example.org:3600/"
        )


async def subdomain_app(scope, receive, send):
    response = JSONResponse({"subdomain": scope["path_params"]["subdomain"]})
    await response(scope, receive, send)


subdomain_router = Router(
    routes=[Host("{subdomain}.example.org", app=subdomain_app, name="subdomains")]
)


def test_subdomain_routing(test_client_factory):
    client = test_client_factory(subdomain_router, base_url="https://esmerald.example.org/")

    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"subdomain": "esmerald"}


def test_subdomain_reverse_urls(test_client_factory):
    client = test_client_factory(subdomain_router, base_url="https://esmerald.example.org/")
    assert (
        client.app.url_path_for(
            "subdomains", subdomain="esmerald", path="/homepage"
        ).make_absolute_url("https://whatever")
        == "https://esmerald.example.org/homepage"
    )


@get("/")
async def echo_urls(request: Request) -> UJSONResponse:
    return UJSONResponse(
        {
            "index": request.url_for("index"),
            "submount": request.url_for("include:submount"),
        }
    )


echo_url_routes = [
    Gateway("/", handler=echo_urls, name="index"),
    Include(
        "/submount",
        name="include",
        routes=[Gateway("/", handler=echo_urls, name="submount")],
    ),
]


def test_url_for_with_root_path(test_client_factory):
    with create_client(
        routes=echo_url_routes,
        base_url="https://www.example.org/",
        root_path="/sub_path",
    ) as client:
        response = client.get("/sub_path")
        assert response.json() == {
            "index": "https://www.example.org/sub_path/",
            "submount": "https://www.example.org/sub_path/submount/",
        }
        response = client.get("/sub_path/submount/")
        assert response.json() == {
            "index": "https://www.example.org/sub_path/",
            "submount": "https://www.example.org/sub_path/submount/",
        }


async def stub_app(scope, receive, send):
    pass  # pragma: no cover


double_mount_routes = [
    Include(
        "/include",
        name="include",
        routes=[Include("/static", app=stub_app, name="static")],
    ),
]


@get("/")
async def url_ok() -> PlainTextResponse:
    return PlainTextResponse("Hello, World!")


def test_url_for_with_double_mount(test_client_factory):
    app = Esmerald(routes=double_mount_routes)
    url = app.url_path_for("include:static", path="123")
    assert url == "/include/static/123"


def test_standalone_route_matches(test_client_factory):
    routes = [Gateway(path="/", handler=url_ok)]

    with create_client(routes=routes) as client:
        response = client.get("/")
        assert response.status_code == 200
        assert response.text == "Hello, World!"


def test_standalone_route_does_not_match(test_client_factory):
    routes = [Gateway("/", handler=url_ok)]

    with create_client(routes=routes) as client:
        response = client.get("/invalid")
        assert response.status_code == 404
        assert response.json()["detail"] == "The resource cannot be found."


@websocket(path="/")
async def ws_helloworld(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_text("Hello, world!")
    await socket.close()


def test_standalone_ws_route_matches(test_client_factory):
    routes = [WebSocketGateway(path="/", handler=ws_helloworld)]

    with create_client(routes=routes) as client:
        with client.websocket_connect("/") as websocket:
            text = websocket.receive_text()
            assert text == "Hello, world!"


def test_standalone_ws_route_does_not_match(test_client_factory):
    routes = [WebSocketGateway(path="/", handler=ws_helloworld)]

    with create_client(routes=routes) as client:
        with pytest.raises(WebSocketDisconnect):
            with client.websocket_connect("/invalid"):
                pass  # pragma: nocover


def test_lifespan_async(test_client_factory):
    startup_complete = False
    shutdown_complete = False

    @get("/")
    async def hello_world(request: Request) -> PlainTextResponse:
        return PlainTextResponse("hello, world")

    async def run_startup() -> None:
        nonlocal startup_complete
        startup_complete = True

    async def run_shutdown() -> None:
        nonlocal shutdown_complete
        shutdown_complete = True

    routes = [Gateway("/", handler=hello_world)]

    assert not startup_complete
    assert not shutdown_complete

    with create_client(
        routes=routes, on_shutdown=[run_shutdown], on_startup=[run_startup]
    ) as client:
        assert startup_complete
        assert not shutdown_complete
        client.get("/")

    assert startup_complete
    assert shutdown_complete


def test_lifespan_state_unsupported(test_client_factory):
    @contextlib.asynccontextmanager
    async def lifespan(app):
        yield {"test": "esmerald"}

    app = Router(
        lifespan=lifespan,
        routes=[Include("/", PlainTextResponse("hello, esmerald"))],
    )

    async def no_state_wrapper(scope, receive, send):
        del scope["state"]
        await app(scope, receive, send)

    with pytest.raises(
        RuntimeError, match='The server does not support "state" in the lifespan scope'
    ):
        with test_client_factory(no_state_wrapper):
            raise AssertionError("Should not be called")  # pragma: no cover


def test_lifespan_sync(test_client_factory):
    startup_complete = False
    shutdown_complete = False

    @get("/")
    def hello_world(request: Request) -> PlainTextResponse:
        return PlainTextResponse("hello, world")

    def run_startup():
        nonlocal startup_complete
        startup_complete = True

    def run_shutdown():
        nonlocal shutdown_complete
        shutdown_complete = True

    routes = [Gateway("/", handler=hello_world)]

    assert not startup_complete
    assert not shutdown_complete

    with create_client(
        routes=routes,
        on_shutdown=[run_shutdown],
        on_startup=[run_startup],
    ) as client:
        assert startup_complete
        assert not shutdown_complete
        client.get("/")

    assert startup_complete
    assert shutdown_complete


def test_raise_on_startup(test_app_client_factory):
    def run_startup():
        raise RuntimeError()

    router = Router(on_startup=[run_startup])
    startup_failed = False

    async def app(scope, receive, send):
        async def _send(message):
            nonlocal startup_failed
            if message["type"] == "lifespan.startup.failed":
                startup_failed = True
            return await send(message)

        await router(scope, receive, _send)

    with pytest.raises(RuntimeError):
        with test_app_client_factory(app):
            pass  # pragma: nocover
    assert startup_failed


def test_raise_on_shutdown(test_app_client_factory):
    def run_shutdown():
        raise RuntimeError()

    app = Router(on_shutdown=[run_shutdown])

    with pytest.raises(RuntimeError):
        with test_app_client_factory(app):
            pass  # pragma: nocover


def test_duplicated_param_names():
    with pytest.raises(
        ValueError,
        match="Duplicated param name id at path /{id}/{id}",
    ):
        Gateway("/{id}/{id}", handler=user)

    with pytest.raises(
        ValueError,
        match="Duplicated param names id, name at path /{id}/{name}/{id}/{name}",
    ):
        Gateway("/{id}/{name}/{id}/{name}", handler=user)


def test_exception_on_mounted_apps(test_app_client_factory):
    class CustomException(Exception):
        """ """

    @get(path="/")
    def exc(request: Request) -> CustomException:
        raise CustomException("Exc")

    sub_app = Esmerald(routes=[Gateway("/", handler=exc)])
    app = Esmerald(routes=[Include("/sub", app=sub_app)])

    client = test_app_client_factory(app)
    response = client.get("/sub/")

    assert "Exception: Exc" in response.text
    assert response.status_code == 500
    assert response.reason_phrase == "Internal Server Error"


@dataclass
class UserIn:
    name: str
    email: str


@pydantic_dataclass
class UserOut:
    name: str
    email: str


def test_response_dataclass(test_app_client_factory):
    @post(path="/user", status_code=200)
    def user(data: UserIn) -> UserIn:
        return data

    data = {"name": "test", "email": "esmerald@esmerald.dev"}
    app = Esmerald(routes=[Gateway(handler=user)])

    client = test_app_client_factory(app)
    response = client.post("/user", json=data)

    assert response.status_code == 200
    assert response.json() == {"name": "test", "email": "esmerald@esmerald.dev"}


def test_response_pydantic_dataclass(test_app_client_factory):
    @post(path="/another-user", status_code=200)
    def another_user(data: UserOut) -> UserOut:
        return data

    data = {"name": "test", "email": "esmerald@esmerald.dev"}
    app = Esmerald(routes=[Gateway(handler=another_user)])

    client = test_app_client_factory(app)
    response = client.post("/another-user", json=data)

    assert response.status_code == 200
    assert response.json() == {"name": "test", "email": "esmerald@esmerald.dev"}
