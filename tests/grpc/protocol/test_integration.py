from __future__ import annotations

import asyncio

import grpc
import pytest
from grpc import aio

from ravyn.testclient import EsmeraldTestClient
from tests.grpc.protocol import greeter_pb2, greeter_pb2_grpc

# Import the Ravyn app and gRPC gateway from service.py
from tests.grpc.protocol.service import (
    GreeterService,
    app,
)


# -------------------------------
# HTTP Integration Tests
# -------------------------------
@pytest.fixture
def http_client() -> EsmeraldTestClient:
    return EsmeraldTestClient(app)


def test_http_sayhello(http_client: EsmeraldTestClient) -> None:
    # Call the HTTP endpoint that triggers GreeterService.SayHello
    response = http_client.post("/grpc/greeterservice/sayhello", json={"name": "World"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, World!"}


def test_http_sayhello_error(http_client: EsmeraldTestClient) -> None:
    response = http_client.post("/grpc/greeterservice/sayhello", json={"name": "error"})
    # Our HTTP gateway maps a gRPC error to an HTTP 400.
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid request"


# -------------------------------
# gRPC Protocol Tests using grpc.aio
# -------------------------------
class GreeterStub:
    """
    A simple gRPC stub that wraps the generated GreeterStub.
    """

    def __init__(self, channel: aio.Channel) -> None:
        self.stub = greeter_pb2_grpc.GreeterStub(channel)

    async def SayHello(self, name: str) -> str:
        request = greeter_pb2.HelloRequest(name=name)
        reply = await self.stub.SayHello(request)
        return reply.message


@pytest.fixture(scope="module")
async def grpc_server_fixture() -> aio.Server:
    # Start the gRPC server separately for protocol tests.
    server = aio.server()
    greeter_pb2_grpc.add_GreeterServicer_to_server(GreeterService(), server)
    server.add_insecure_port("127.0.0.1:50051")
    await server.start()
    await asyncio.sleep(0.1)
    yield server
    await server.stop(0)


@pytest.mark.anyio
async def test_grpc_sayhello(grpc_server_fixture: aio.Server) -> None:
    async with aio.insecure_channel("127.0.0.1:50051") as channel:
        stub = GreeterStub(channel)
        message = await stub.SayHello("GRPC")
        assert message == "Hello, GRPC!"


@pytest.mark.anyio
async def test_grpc_sayhello_error(grpc_server_fixture: aio.Server) -> None:
    async with aio.insecure_channel("127.0.0.1:50051") as channel:
        stub = GreeterStub(channel)
        with pytest.raises(aio.AioRpcError) as exc_info:
            await stub.SayHello("error")
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
        assert exc_info.value.details() == "Invalid request"
