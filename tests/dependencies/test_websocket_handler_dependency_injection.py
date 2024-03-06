from asyncio import sleep
from typing import Any, Dict

import pytest
from lilya.websockets import WebSocketDisconnect

from esmerald.injector import Inject
from esmerald.routing.apis.views import APIView
from esmerald.routing.gateways import WebSocketGateway
from esmerald.routing.handlers import websocket
from esmerald.testclient import create_client
from esmerald.websockets import WebSocket


def router_first_dependency() -> bool:  # pragma: no cover
    return True


async def router_second_dependency() -> bool:
    await sleep(0.1)
    return False


def controller_first_dependency(headers: Dict[str, Any]) -> dict:  # pragma: no cover
    assert headers
    return {}  # pragma: no cover


async def controller_second_dependency(socket: WebSocket) -> dict:
    assert socket
    await sleep(0.1)
    return {}


def local_method_first_dependency(query_param: int) -> int:
    assert isinstance(query_param, int)
    return query_param


def local_method_second_dependency(path_param: str) -> str:
    assert isinstance(path_param, str)
    return path_param


test_path = "/test"


class FirstController(APIView):
    path = test_path
    dependencies = {
        "first": Inject(controller_first_dependency),
        "second": Inject(controller_second_dependency),
    }

    @websocket(
        path="/{path_param:str}",
        dependencies={
            "first": Inject(local_method_first_dependency),
        },
    )
    async def test_method(self, socket: WebSocket, first: int, second: dict, third: bool) -> None:
        await socket.accept()
        msg = await socket.receive_json()
        assert msg
        assert socket
        assert isinstance(first, int)
        assert isinstance(second, dict)
        assert third is False
        await socket.close()


def test_controller_dependency_injection() -> None:
    client = create_client(
        routes=[WebSocketGateway(path="/", handler=FirstController)],
        dependencies={
            "second": Inject(router_first_dependency),
            "third": Inject(router_second_dependency),
        },
    )
    with client.websocket_connect(f"{test_path}/abcdef?query_param=12345") as ws:
        ws.send_json({"data": "123"})


def test_function_dependency_injection() -> None:
    @websocket(
        path=test_path + "/{path_param:str}",
        dependencies={
            "first": Inject(local_method_first_dependency),
            "third": Inject(local_method_second_dependency),
        },
    )
    async def test_function(socket: WebSocket, first: int, second: bool, third: str) -> None:
        await socket.accept()
        assert socket
        msg = await socket.receive_json()
        assert msg
        assert isinstance(first, int)
        assert second is False
        assert isinstance(third, str)
        await socket.close()

    client = create_client(
        WebSocketGateway(path="/", handler=test_function),
        dependencies={
            "first": Inject(router_first_dependency),
            "second": Inject(router_second_dependency),
        },
    )
    with client.websocket_connect(f"{test_path}/abcdef?query_param=12345") as ws:
        ws.send_json({"data": "123"})


def test_dependency_isolation() -> None:  # pragma: no cover
    class SecondController(APIView):
        path = "/second"

        @websocket(path="/")
        async def test_method(self, socket: WebSocket, first: dict) -> None:
            await socket.accept()

    client = create_client(
        [
            WebSocketGateway(path="/", handler=FirstController),
            WebSocketGateway(path="/", handler=SecondController),
        ]
    )
    with pytest.raises(WebSocketDisconnect), client.websocket_connect(
        "/second/abcdef?query_param=12345"
    ) as ws:
        ws.send_json({"data": "123"})
