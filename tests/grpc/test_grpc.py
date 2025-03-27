from __future__ import annotations

from typing import Any

import pytest
from grpclib.exceptions import GRPCError, Status

from esmerald import Esmerald
from esmerald.grpc.gateway import GrpcGateway
from esmerald.grpc.register import register_grpc_http_routes
from esmerald.testclient import EsmeraldTestClient


# 1️⃣ Mock gRPC Service
# 1️⃣ Define a Proper gRPC Service
class MockGrpcService:
    async def SayHello(self, request: dict[str, Any]) -> dict[str, Any]:
        if request.get("name") == "error":
            raise GRPCError(Status.INVALID_ARGUMENT, "Invalid request")
        return {"message": f"Hello, {request['name']}!"}

    async def SayGoodbye(self, request: dict[str, Any]) -> dict[str, Any]:
        return {"message": f"Goodbye, {request['name']}!"}

    @classmethod
    def __mapping__(cls) -> dict[str, Any]:
        return {
            "SayHello": cls.SayHello,
            "SayGoodbye": cls.SayGoodbye,
        }


grpc_gateway = GrpcGateway(path="/grpc", services=[MockGrpcService])
app = Esmerald(routes=[], on_startup=[grpc_gateway.startup], on_shutdown=[grpc_gateway.shutdown])
register_grpc_http_routes(app=app, grpc_gateways=[grpc_gateway])


@pytest.fixture
def client():
    return EsmeraldTestClient(app)


# 3️⃣ Test HTTP → gRPC Mapping
def test_grpc_http_success(client):
    response = client.post("/grpc/mockgrpcservice/sayhello", json={"name": "Esmerald"})
    assert response.status_code == 200
    assert response.json() == {"message": "Hello, Esmerald!"}


def test_grpc_http_goodbye(client):
    response = client.post("/grpc/mockgrpcservice/saygoodbye", json={"name": "Esmerald"})
    assert response.status_code == 200
    assert response.json() == {"message": "Goodbye, Esmerald!"}


def xtest_grpc_http_error(client):
    response = client.post("/grpc/mockgrpcservice/sayhello", json={"name": "error"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid request"
