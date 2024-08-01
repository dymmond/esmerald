from typing import Generic, Optional, Type, TypeVar

from pydantic import BaseModel

from esmerald.injector import Inject
from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import get
from esmerald.testclient import create_client

T = TypeVar("T")


class Store(BaseModel, Generic[T]):
    """Abstract store."""

    model: Type[T]

    def get(self, value_id: str) -> Optional[T]:  # pragma: no cover
        raise NotImplementedError


class Item(BaseModel):
    name: str


class DictStore(Store[Item]):
    """In-memory store implementation."""

    def get(self, value_id: str) -> Optional[Item]:
        return None


@get("/")
async def root(store: DictStore) -> Optional[Item]:
    assert isinstance(store, DictStore)
    return store.get("0")


def get_item_store() -> DictStore:
    return DictStore(model=Item)  # type: ignore


def test_generic_model_injection() -> None:
    with create_client(
        routes=[Gateway(path="/", handler=root)],
        dependencies={"store": Inject(get_item_store, use_cache=True)},
    ) as client:
        response = client.get("/openapi.json")

        assert response.json() == {
            "openapi": "3.1.0",
            "info": {
                "title": "Esmerald",
                "summary": "Esmerald application",
                "description": "Highly scalable, performant, easy to learn and for every application.",
                "contact": {"name": "admin", "email": "admin@myapp.com"},
                "version": client.app.version,
            },
            "servers": [{"url": "/"}],
            "paths": {
                "/": {
                    "get": {
                        "summary": "Root",
                        "operationId": "root__get",
                        "responses": {
                            "200": {
                                "description": "Successful response",
                                "content": {"application/json": {"schema": {"type": "string"}}},
                            }
                        },
                        "deprecated": False,
                    }
                }
            },
        }
