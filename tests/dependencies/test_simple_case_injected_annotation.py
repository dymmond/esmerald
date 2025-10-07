from typing import TYPE_CHECKING, List

from ravyn import post
from ravyn.injector import Inject
from ravyn.routing.controllers import Controller
from ravyn.routing.gateways import Gateway
from ravyn.testclient import create_client
from tests.dependencies.samples import DocumentService

if TYPE_CHECKING:
    from tests.dependencies.samples import DocumentCreateDTO


class DocumentAPIView(Controller):
    tags: List[str] = ["Document"]
    dependencies = {
        "service": Inject(DocumentService),
    }

    @post("/")
    async def create(
        self, data: "DocumentCreateDTO", service: "DocumentService"
    ) -> "DocumentCreateDTO":
        return await service.create(data)


def test_injection():
    with create_client(routes=[Gateway(handler=DocumentAPIView)]) as client:
        response = client.post("/", json={"name": "test", "content": "test"})
        assert response.status_code == 201
        assert response.json() == {"name": "test", "content": "test"}
