from pydantic import BaseModel

from ravyn import Controller, Gateway, post
from ravyn.testclient import create_client
from ravyn.utils.decorators import cache


class Item(BaseModel):
    id: int
    name: str


def test_basic_caching_memory(memory_cache, test_client_factory) -> None:
    @post("/items")
    @cache(backend=memory_cache)
    async def items_view(data: Item) -> Item:
        return data

    with create_client(routes=[Gateway(handler=items_view)]) as client:
        response = client.post("/items", json={"id": 1, "name": "Test Item"})
        assert response.status_code == 201
        assert response.json() == {"id": 1, "name": "Test Item"}


def test_controller_caching(memory_cache, test_client_factory) -> None:
    class ItemsController(Controller):
        path = "/items"

        @post()
        @cache(backend=memory_cache)
        async def create_item(self, data: Item) -> Item:
            return data

    with create_client(routes=[Gateway(handler=ItemsController)], debug=True) as client:
        response = client.post("/items", json={"id": 1, "name": "Test Item"})
        assert response.status_code == 201
        assert response.json() == {"id": 1, "name": "Test Item"}
