from typing import Generic, Optional, Type, TypeVar

from lilya.status import HTTP_200_OK
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
def root(store: DictStore) -> Optional[Item]:
    assert isinstance(store, DictStore)
    return store.get("0")


def get_item_store() -> DictStore:
    return DictStore(model=Item)  # type: ignore


def test_generic_model_injection() -> None:
    with create_client(
        routes=[Gateway(path="/", handler=root)],
        dependencies={"store": Inject(get_item_store, use_cache=True)},
    ) as client:
        response = client.get("/")
        assert response.status_code == HTTP_200_OK
