from __future__ import annotations

from typing import List

from esmerald import post
from esmerald.injector import Inject
from esmerald.routing.apis.views import APIView
from esmerald.routing.gateways import Gateway
from esmerald.testclient import create_client
from tests.dependencies.samples import DocumentCreateDTO, DocumentService


class DocumentAPIView(APIView):
    tags: List[str] = ["Document"]
    dependencies = {
        "service": Inject(DocumentService),
    }

    @post("/")
    async def create(
        self, data: DocumentCreateDTO, service: DocumentService
    ) -> "DocumentCreateDTO":
        return await service.create(data)


def test_injection():

    with create_client(routes=[Gateway(handler=DocumentAPIView)]) as client:
        response = client.post("/", json={"name": "test", "content": "test"})
        assert response.status_code == 201
        assert response.json() == {"name": "test", "content": "test"}
