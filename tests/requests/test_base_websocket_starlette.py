"""The tests in this file were adapted from:

https://github.com/encode/lilya/blob/master/tests/test_websockets.py
"""

import sys

import anyio
import pytest
from lilya import status
from lilya.types import Receive, Scope, Send
from lilya.websockets import WebSocketDisconnect, WebSocketState

from esmerald.testclient import EsmeraldTestClient
from esmerald.websockets import WebSocket


def test_websocket_url(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        await websocket.send_json({"url": str(websocket.url)})
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/123?a=abc") as websocket:
        data = websocket.receive_json()
        assert data == {"url": "ws://testserver/123?a=abc"}


def test_websocket_binary_json(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        message = await websocket.receive_json(mode="binary")
        await websocket.send_json(message, mode="binary")
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/123?a=abc") as websocket:
        websocket.send_json({"test": "data"}, mode="binary")
        data = websocket.receive_json(mode="binary")
        assert data == {"test": "data"}


def test_websocket_query_params(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        query_params = dict(websocket.query_params)
        await websocket.accept()
        await websocket.send_json({"params": query_params})
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/?a=abc&b=456") as websocket:
        data = websocket.receive_json()
        assert data == {"params": {"a": "abc", "b": "456"}}


@pytest.mark.skipif(
    any(module in sys.modules for module in ("brotli", "brotlicffi")),
    reason='urllib3 includes "br" to the "accept-encoding" headers.',
)
def test_websocket_headers(test_client_factory):  # pragma: no cover
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        headers = dict(websocket.headers)
        await websocket.accept()
        await websocket.send_json({"headers": headers})
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        expected_headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate",
            "connection": "upgrade",
            "host": "testserver",
            "user-agent": "testclient",
            "sec-websocket-key": "testserver==",
            "sec-websocket-version": "13",
        }
        data = websocket.receive_json()
        assert data == {"headers": expected_headers}


def test_websocket_port(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        await websocket.send_json({"port": websocket.url.port})
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("ws://example.com:123/123?a=abc") as websocket:
        data = websocket.receive_json()
        assert data == {"port": 123}


def test_websocket_send_and_receive_text(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        data = await websocket.receive_text()
        await websocket.send_text("Message was: " + data)
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        websocket.send_text("Hello, world!")
        data = websocket.receive_text()
        assert data == "Message was: Hello, world!"


def test_websocket_send_and_receive_bytes(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        data = await websocket.receive_bytes()
        await websocket.send_bytes(b"Message was: " + data)
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        websocket.send_bytes(b"Hello, world!")
        data = websocket.receive_bytes()
        assert data == b"Message was: Hello, world!"


def test_websocket_send_and_receive_json(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        data = await websocket.receive_json()
        await websocket.send_json({"message": data})
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        websocket.send_json({"hello": "world"})
        data = websocket.receive_json()
        assert data == {"message": {"hello": "world"}}


def test_websocket_iter_text(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        async for data in websocket.iter_text():
            await websocket.send_text("Message was: " + data)

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        websocket.send_text("Hello, world!")
        data = websocket.receive_text()
        assert data == "Message was: Hello, world!"


def test_websocket_iter_bytes(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        async for data in websocket.iter_bytes():
            await websocket.send_bytes(b"Message was: " + data)

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        websocket.send_bytes(b"Hello, world!")
        data = websocket.receive_bytes()
        assert data == b"Message was: Hello, world!"


def test_websocket_iter_json(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        async for data in websocket.iter_json():
            await websocket.send_json({"message": data})

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        websocket.send_json({"hello": "world"})
        data = websocket.receive_json()
        assert data == {"message": {"hello": "world"}}


def test_websocket_concurrency_pattern(test_client_factory):
    stream_send, stream_receive = anyio.create_memory_object_stream()

    async def reader(websocket):
        async with stream_send:
            async for data in websocket.iter_json():
                await stream_send.send(data)

    async def writer(websocket):
        async with stream_receive:
            async for message in stream_receive:
                await websocket.send_json(message)

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        async with anyio.create_task_group() as task_group:
            task_group.start_soon(reader, websocket)
            await writer(websocket)
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        websocket.send_json({"hello": "world"})
        data = websocket.receive_json()
        assert data == {"hello": "world"}


def test_client_close(test_client_factory):
    close_code = None

    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        nonlocal close_code
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        try:
            await websocket.receive_text()
        except WebSocketDisconnect as exc:
            close_code = exc.code

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        websocket.close(code=status.WS_1001_GOING_AWAY)
    assert close_code == status.WS_1001_GOING_AWAY


def test_application_close(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        await websocket.close(status.WS_1001_GOING_AWAY)

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        with pytest.raises(WebSocketDisconnect) as exc:
            websocket.receive_text()
        assert exc.value.code == status.WS_1001_GOING_AWAY


def test_rejected_connection(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.close(status.WS_1001_GOING_AWAY)

    client = EsmeraldTestClient(app)
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect("/"):
            pass  # pragma: nocover
    assert exc.value.code == status.WS_1001_GOING_AWAY


def test_subprotocol(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        assert websocket["subprotocols"] == ["soap", "wamp"]
        await websocket.accept(subprotocol="wamp")
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/", subprotocols=["soap", "wamp"]) as websocket:
        assert websocket.accepted_subprotocol == "wamp"


def test_additional_headers(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept(headers=[(b"additional", b"header")])
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        assert websocket.extra_headers == [(b"additional", b"header")]


def test_no_additional_headers(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        await websocket.close()

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        assert websocket.extra_headers == []


def test_websocket_exception(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        raise AssertionError()

    client = EsmeraldTestClient(app)
    with pytest.raises(AssertionError):
        with client.websocket_connect("/123?a=abc"):
            pass  # pragma: nocover


def test_duplicate_close(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        await websocket.close()
        await websocket.close()

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/"):
            pass  # pragma: nocover


def test_duplicate_disconnect(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        message = await websocket.receive()
        assert message["type"] == "websocket.disconnect"
        message = await websocket.receive()

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/") as websocket:
            websocket.close()


def test_websocket_scope_interface():
    """
    A WebSocket can be instantiated with a scope, and presents a `Mapping`
    interface.
    """

    async def mock_receive():
        pass  # pragma: no cover

    async def mock_send(message):
        pass  # pragma: no cover

    websocket = WebSocket(
        {"type": "websocket", "path": "/abc/", "headers": []},
        receive=mock_receive,
        send=mock_send,
    )
    assert websocket["type"] == "websocket"
    assert dict(websocket) == {"type": "websocket", "path": "/abc/", "headers": []}
    assert len(websocket) == 3

    # check __eq__ and __hash__
    assert websocket != WebSocket(
        {"type": "websocket", "path": "/abc/", "headers": []},
        receive=mock_receive,
        send=mock_send,
    )
    # deepcode ignore CopyPasteError/test: This is for testing purposes
    assert websocket == websocket
    assert websocket in {websocket}
    # deepcode ignore CopyPasteError/test: This is for testing purposes
    assert {websocket} == {websocket}


def test_websocket_close_reason(test_client_factory) -> None:
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        await websocket.close(code=status.WS_1001_GOING_AWAY, reason="Going Away")

    client = EsmeraldTestClient(app)
    with client.websocket_connect("/") as websocket:
        with pytest.raises(WebSocketDisconnect) as exc:
            websocket.receive_text()
        assert exc.value.code == status.WS_1001_GOING_AWAY
        assert exc.value.reason == "Going Away"


def test_send_json_invalid_mode(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        await websocket.send_json({}, mode="invalid")

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/"):
            pass  # pragma: nocover


def test_receive_json_invalid_mode(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        await websocket.receive_json(mode="invalid")

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/"):
            pass  # pragma: nocover


def test_receive_text_before_accept(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.receive_text()

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/"):
            pass  # pragma: nocover


def test_receive_bytes_before_accept(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.receive_bytes()

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/"):
            pass  # pragma: nocover


def test_receive_json_before_accept(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.receive_json()

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/"):
            pass  # pragma: nocover


def test_send_before_accept(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.send({"type": "websocket.send"})

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/"):
            pass  # pragma: nocover


def test_send_wrong_message_type(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.send({"type": "websocket.accept"})
        await websocket.send({"type": "websocket.accept"})

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/"):
            pass  # pragma: nocover


def test_receive_before_accept(test_client_factory):
    async def app(scope: Scope, receive: Receive, send: Send) -> None:
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        websocket.client_state = WebSocketState.CONNECTING
        await websocket.receive()

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/") as websocket:
            websocket.send({"type": "websocket.send"})


def test_receive_wrong_message_type(test_client_factory):
    async def app(scope, receive, send):
        websocket = WebSocket(scope, receive=receive, send=send)
        await websocket.accept()
        await websocket.receive()

    client = EsmeraldTestClient(app)
    with pytest.raises(RuntimeError):
        with client.websocket_connect("/") as websocket:
            websocket.send({"type": "websocket.connect"})
