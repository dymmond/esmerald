from typing import AsyncGenerator, List, Type

import edgy
import pytest
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from esmerald import Esmerald, post
from esmerald.conf import settings
from esmerald.injector import Inject
from esmerald.routing.apis.views import APIView
from esmerald.routing.gateways import Gateway

models = settings.edgy_registry
pytestmark = pytest.mark.anyio


class Document(edgy.Model):
    name = edgy.CharField(max_length=255)
    content = edgy.TextField()

    class Meta:
        registry = models


class DocumentCreateDTO(BaseModel):
    name: str
    content: str


class DocumentService:
    def __init__(self, model: Type[edgy.Model] = Document):
        self.model = model

    async def create(self, dto: DocumentCreateDTO) -> Document:
        return await self.model.query.create(**dto.model_dump())


class DocumentAPIView(APIView):
    tags: List[str] = ["Document"]
    dependencies = {
        "service": Inject(DocumentService),
    }

    @post("/")
    async def create(self, data: DocumentCreateDTO, service: DocumentService) -> Document:
        return await service.create(data)


@pytest.fixture(autouse=True, scope="module")
async def create_test_database():
    try:
        await models.create_all()
        yield
        await models.drop_all()
    except Exception:
        pytest.skip("No database available")


@pytest.fixture(autouse=True)
async def rollback_transactions():
    with models.database.force_rollback():
        async with models.database:
            yield


@pytest.fixture()
def app():
    app = Esmerald(routes=[Gateway(handler=DocumentAPIView)])
    return app


@pytest.fixture()
async def async_client(app) -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


async def test_injection(async_client):
    response = await async_client.post("/", json={"name": "test", "content": "test"})
    assert response.status_code == 201
    jsonob = response.json()
    jsonob.pop("id")
    assert jsonob == {"name": "test", "content": "test"}
