"""The tests in this file were adapted from:

https://github.com/encode/starlette/blob/master/tests/test_requests.py.
"""

from typing import Any, Optional

import anyio
import pytest
from lilya._internal._message import Address
from lilya.datastructures import State
from starlette.status import HTTP_200_OK
from starlette.types import Receive, Send

from esmerald.enums import MediaType
from esmerald.exceptions import InternalServerError
from esmerald.requests import ClientDisconnect, Request, empty_send
from esmerald.responses import JSONResponse, PlainText, Response
from esmerald.testclient import EsmeraldTestClient


def test_request_url(test_client_factory) -> None:
    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope, receive)
        data = {"method": request.method, "url": str(request.url)}
        response = Response(content=data, status_code=HTTP_200_OK, media_type=MediaType.JSON)
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.get("/123?a=abc")
    assert response.json() == {"method": "GET", "url": "http://testserver/123?a=abc"}

    response = client.get("https://example.org:123/")
    assert response.json() == {"method": "GET", "url": "https://example.org:123/"}


def test_request_query_params(test_client_factory) -> None:
    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope, receive)
        params = dict(request.query_params)
        response = Response(
            content={"params": params},
            status_code=HTTP_200_OK,
            media_type=MediaType.JSON,
        )
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.get("/?a=123&b=456")
    assert response.json() == {"params": {"a": "123", "b": "456"}}


def test_request_headers(test_client_factory) -> None:
    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope, receive)
        headers = dict(request.headers)
        response = Response(
            content={"headers": headers},
            status_code=HTTP_200_OK,
            media_type=MediaType.JSON,
        )
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.get("/", headers={"host": "example.org"})
    assert response.json() == {
        "headers": {
            "host": "example.org",
            "user-agent": "testclient",
            "accept-encoding": "gzip, deflate, br",
            "accept": "*/*",
            "connection": "keep-alive",
        }
    }


@pytest.mark.parametrize(
    "scope,expected_client",
    [
        ({"client": ["client", 42]}, Address("client", 42)),
        ({"client": None}, None),
        ({}, None),
    ],
)
def test_request_client(scope: Any, expected_client: Optional[Address]) -> None:
    scope.update({"type": "http"})  # required by Request's constructor
    client = Request(scope).client
    assert client == expected_client


def test_request_body(test_client_factory) -> None:
    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope, receive)
        body = await request.body()
        response = Response(
            content={"body": body.decode()},
            status_code=HTTP_200_OK,
            media_type=MediaType.JSON,
        )
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore

    response = client.get("/")
    assert response.json() == {"body": ""}

    response = client.post("/", json={"a": "123"})
    assert response.json() == {"body": '{"a": "123"}'}

    response = client.post("/", data="abc")
    assert response.json() == {"body": "abc"}


def test_request_stream(test_client_factory) -> None:
    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope, receive)
        body = b""
        async for chunk in request.stream():
            body += chunk
        response = Response(
            content={"body": body.decode()},
            status_code=HTTP_200_OK,
            media_type=MediaType.JSON,
        )
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore

    response = client.get("/")
    assert response.json() == {"body": ""}

    response = client.post("/", json={"a": "123"})
    assert response.json() == {"body": '{"a": "123"}'}

    response = client.post("/", data="abc")
    assert response.json() == {"body": "abc"}


def test_request_form_urlencoded(test_client_factory) -> None:
    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope, receive)
        form = await request.form()
        response = JSONResponse({"form": dict(form)})
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore

    response = client.post("/", data={"abc": "123 @"})
    assert response.json() == {"form": {"abc": "123 @"}}


def test_request_body_then_stream(test_client_factory) -> None:
    async def app(scope: "Any", receive: "Receive", send: "Send") -> None:
        request = Request(scope, receive)
        body = await request.body()
        chunks = b""
        async for chunk in request.stream():
            chunks += chunk
        response = JSONResponse({"body": body.decode(), "stream": chunks.decode()})
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore

    response = client.post("/", data="abc")
    assert response.json() == {"body": "abc", "stream": "abc"}


def test_request_json() -> None:
    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope, receive)
        data = await request.json()
        response = Response(
            content={"json": data}, status_code=HTTP_200_OK, media_type=MediaType.JSON
        )
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.post("/", json={"a": "123"})
    assert response.json() == {"json": {"a": "123"}}


def test_request_stream_then_body(test_client_factory):
    async def app(scope, receive, send):
        request = Request(scope, receive)
        chunks = b""
        async for chunk in request.stream():
            chunks += chunk
        try:
            body = await request.body()
        except RuntimeError:
            body = b"<stream consumed>"
        response = JSONResponse({"body": body.decode(), "stream": chunks.decode()})
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)
    response = client.post("/", data="abc")
    assert response.json() == {"body": "<stream consumed>", "stream": "abc"}


def test_request_raw_path_one() -> None:
    async def app(scope, receive, send):
        request = Request(scope, receive)
        data = await request.json()
        response = JSONResponse({"json": data})
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.post("/", json={"a": "123"})
    assert response.json() == {"json": {"a": "123"}}


def test_request_scope_interface():
    """
    A Request can be instantiated with a scope, and presents a `Mapping`
    interface.
    """
    request = Request({"type": "http", "method": "GET", "path": "/abc/"})
    assert request["method"] == "GET"
    assert dict(request) == {"type": "http", "method": "GET", "path": "/abc/"}
    assert len(request) == 3


def test_request_raw_path(test_client_factory):
    async def app(scope, receive, send):
        request = Request(scope, receive)
        path = request.scope["path"]
        raw_path = request.scope["raw_path"]
        response = PlainText(f"{path}, {raw_path}")
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)
    response = client.get("/he%2Fllo")
    assert response.text == "/he/llo, b'/he%2Fllo'"


def test_request_without_setting_receive() -> None:
    """If Request is instantiated without the 'receive' channel, then .body()
    is not available."""

    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope)
        try:
            data = await request.json()
        except RuntimeError:
            data = "Receive channel not available"
        response = Response(
            content={"json": data}, status_code=HTTP_200_OK, media_type=MediaType.JSON
        )
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.post("/", json={"a": "123"})
    assert response.json() == {"json": "Receive channel not available"}


async def test_request_disconnect() -> None:  # pragma: no cover
    """If a client disconnect occurs while reading request body then
    InternalServerError should be raised."""

    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope, receive)
        await request.body()

    async def receiver():
        return {"type": "http.disconnect"}

    scope = {"type": "http", "method": "POST", "path": "/"}
    with pytest.raises(InternalServerError):
        await app(scope, receiver, empty_send)


def test_request_anyio_disconnect(anyio_backend_name, anyio_backend_options):
    """
    If a client disconnect occurs while reading request body
    then ClientDisconnect should be raised.
    """

    async def app(scope, receive, send):
        request = Request(scope, receive)
        await request.body()

    async def receiver():
        return {"type": "http.disconnect"}

    scope = {"type": "http", "method": "POST", "path": "/"}
    with pytest.raises(ClientDisconnect):
        anyio.run(
            app,
            scope,
            receiver,
            None,
            backend=anyio_backend_name,
            backend_options=anyio_backend_options,
        )


def test_request_is_disconnected(test_client_factory):
    """
    If a client disconnect occurs while reading request body
    then ClientDisconnect should be raised.
    """
    disconnected_after_response = None

    async def app(scope, receive, send):
        nonlocal disconnected_after_response

        request = Request(scope, receive)
        await request.body()
        disconnected = await request.is_disconnected()
        response = JSONResponse({"disconnected": disconnected})
        await response(scope, receive, send)
        disconnected_after_response = await request.is_disconnected()

    client = EsmeraldTestClient(app)
    response = client.get("/")
    assert response.json() == {"disconnected": False}
    assert disconnected_after_response


def test_request_state_object() -> None:
    scope = {"state": {"old": "foo"}}

    s = State(scope["state"])

    s.new = "value"
    assert s.new == "value"

    del s.new

    with pytest.raises(AttributeError):
        s.new  # noqa


def test_request_state() -> None:
    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        scope["state"] = {}
        request = Request(scope, receive)
        request.state.example = 123
        response = Response(
            content={"state.example": request.state.example},
            status_code=HTTP_200_OK,
            media_type=MediaType.JSON,
        )
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.get("/123?a=abc")
    assert response.json() == {"state.example": 123}


def test_request_cookies() -> None:
    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope, receive)
        mycookie = request.cookies.get("mycookie")
        if mycookie:
            response = Response(mycookie, media_type="text/plain")
        else:
            response = Response("Hello, world!", media_type="text/plain")
            response.set_cookie("mycookie", "Hello, cookies!")

        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.get("/")
    assert response.text == "Hello, world!"
    response = client.get("/")
    assert response.text == "Hello, cookies!"


def test_chunked_encoding() -> None:
    async def app(scope, receive, send):
        request = Request(scope, receive)
        body = await request.body()
        response = JSONResponse({"body": body.decode()})
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore

    def post_body():
        yield b"foo"
        yield b"bar"

    response = client.post("/", data=post_body())
    assert response.json() == {"body": "foobar"}


def test_cookie_lenient_parsing(test_client_factory):
    """
    The following test is based on a cookie set by Okta, a well-known authorization
    service. It turns out that it's common practice to set cookies that would be
    invalid according to the spec.
    """
    tough_cookie = (
        "provider-oauth-nonce=validAsciiblabla; "
        'okta-oauth-redirect-params={"responseType":"code","state":"somestate",'
        '"nonce":"somenonce","scopes":["openid","profile","email","phone"],'
        '"urls":{"issuer":"https://subdomain.okta.com/oauth2/authServer",'
        '"authorizeUrl":"https://subdomain.okta.com/oauth2/authServer/v1/authorize",'
        '"userinfoUrl":"https://subdomain.okta.com/oauth2/authServer/v1/userinfo"}}; '
        "importantCookie=importantValue; sessionCookie=importantSessionValue"
    )
    expected_keys = {
        "importantCookie",
        "okta-oauth-redirect-params",
        "provider-oauth-nonce",
        "sessionCookie",
    }

    async def app(scope, receive, send):
        request = Request(scope, receive)
        response = JSONResponse({"cookies": request.cookies})
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)
    response = client.get("/", headers={"cookie": tough_cookie})
    result = response.json()
    assert len(result["cookies"]) == 4
    assert set(result["cookies"].keys()) == expected_keys


@pytest.mark.parametrize(
    "set_cookie,expected",
    [
        ("chips=ahoy; vienna=finger", {"chips": "ahoy", "vienna": "finger"}),
        # all semicolons are delimiters, even within quotes
        (
            'keebler="E=mc2; L=\\"Loves\\"; fudge=\\012;"',
            {"keebler": '"E=mc2', "L": '\\"Loves\\"', "fudge": "\\012", "": '"'},
        ),
        # Illegal cookies that have an '=' char in an unquoted value.
        ("keebler=E=mc2", {"keebler": "E=mc2"}),
        # Cookies with ':' character in their name.
        ("key:term=value:term", {"key:term": "value:term"}),
        # Cookies with '[' and ']'.
        ("a=b; c=[; d=r; f=h", {"a": "b", "c": "[", "d": "r", "f": "h"}),
        # Cookies that RFC6265 allows.
        ("a=b; Domain=example.com", {"a": "b", "Domain": "example.com"}),
        # parse_cookie() keeps only the last cookie with the same name.
        ("a=b; h=i; a=c", {"a": "c", "h": "i"}),
    ],
)
def test_cookies_edge_cases(set_cookie, expected, test_client_factory):
    async def app(scope, receive, send):
        request = Request(scope, receive)
        response = JSONResponse({"cookies": request.cookies})
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)
    response = client.get("/", headers={"cookie": set_cookie})
    result = response.json()
    assert result["cookies"] == expected


@pytest.mark.parametrize(
    "set_cookie,expected",
    [
        # Chunks without an equals sign appear as unnamed values per
        # https://bugzilla.mozilla.org/show_bug.cgi?id=169091
        (
            "abc=def; unnamed; django_language=en",
            {"": "unnamed", "abc": "def", "django_language": "en"},
        ),
        # Even a double quote may be an unamed value.
        ('a=b; "; c=d', {"a": "b", "": '"', "c": "d"}),
        # Spaces in names and values, and an equals sign in values.
        ("a b c=d e = f; gh=i", {"a b c": "d e = f", "gh": "i"}),
        # More characters the spec forbids.
        ('a   b,c<>@:/[]?{}=d  "  =e,f g', {"a   b,c<>@:/[]?{}": 'd  "  =e,f g'}),
        # Unicode characters. The spec only allows ASCII.
        # ("saint=André Bessette", {"saint": "André Bessette"}),
        # Browsers don't send extra whitespace or semicolons in Cookie headers,
        # but cookie_parser() should parse whitespace the same way
        # document.cookie parses whitespace.
        # ("  =  b  ;  ;  =  ;   c  =  ;  ", {"": "b", "c": ""}),
    ],
)
def test_cookies_invalid(set_cookie, expected, test_client_factory):
    """
    Cookie strings that are against the RFC6265 spec but which browsers will send if set
    via document.cookie.
    """

    async def app(scope, receive, send):
        request = Request(scope, receive)
        response = JSONResponse({"cookies": request.cookies})
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)
    response = client.get("/", headers={"cookie": set_cookie})
    result = response.json()
    assert result["cookies"] == expected


def test_request_send_push_promise() -> None:
    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        # the server is push-enabled
        scope["extensions"]["http.response.push"] = {}

        request = Request(scope, receive, send)
        await request.send_push_promise("/style.css")

        response = JSONResponse({"json": "OK"})
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.get("/")
    assert response.json() == {"json": "OK"}


def test_request_send_push_promise_without_push_extension() -> None:
    """If server does not support the `http.response.push` extension,

    .send_push_promise() does nothing.
    """

    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        request = Request(scope)
        await request.send_push_promise("/style.css")

        response = JSONResponse({"json": "OK"})
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.get("/")
    assert response.json() == {"json": "OK"}


def test_request_send_push_promise_without_setting_send(test_client_factory) -> None:
    """If Request is instantiated without the send channel, then.

    .send_push_promise() is not available.
    """

    async def app(scope: Any, receive: "Receive", send: "Send") -> None:
        # the server is push-enabled
        scope["extensions"]["http.response.push"] = {}

        data = "OK"
        request = Request(scope)
        try:
            await request.send_push_promise("/style.css")
        except RuntimeError:
            data = "Send channel not available"
        response = Response(
            content={"json": data}, status_code=HTTP_200_OK, media_type=MediaType.JSON
        )
        await response(scope, receive, send)

    client = EsmeraldTestClient(app)  # type: ignore
    response = client.get("/")
    assert response.json() == {"json": "Send channel not available"}
