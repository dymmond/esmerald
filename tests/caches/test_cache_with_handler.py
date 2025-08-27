from uuid import UUID, uuid4
from pydantic import BaseModel

from esmerald import Controller, Gateway, get, post, put, patch, delete, JSONResponse, JSON
from esmerald.testclient import create_client
from esmerald.utils.decorators import cache


class Item(BaseModel):
    id: int
    name: str

class ItemWithUUID(BaseModel):
    id: UUID
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


def test_controller_caching_with_uuid(memory_cache, test_client_factory) -> None:
    class ItemsUUIDController(Controller):
        path = "/items"

        @get("/{item_id}")
        @cache(backend=memory_cache)
        async def get_item(self, item_id: UUID) -> ItemWithUUID:
            return {"id": item_id, "name": "Test Item"}

        @post()
        @cache(backend=memory_cache)
        async def create_item_with_JSONResponse(self, data: ItemWithUUID) -> JSONResponse:
            return JSONResponse(content=data)

        @put("/{item_id}")
        @cache(backend=memory_cache)
        async def update_item(self, item_id: UUID, data: ItemWithUUID) -> ItemWithUUID:
            return {"id": item_id, "name": data.name}

        @patch("/{item_id}")
        @cache(backend=memory_cache)
        async def update_item(self, item_id: UUID, data: ItemWithUUID) -> ItemWithUUID:
            return {"id": item_id, "name": data.name}

        @delete("/{item_id}")
        @cache(backend=memory_cache)
        async def delete_item(self, item_id: UUID) -> None:
            return None

        

        @post("/items")
        @cache(backend=memory_cache)
        async def create_item(self, data: ItemWithUUID) -> ItemWithUUID:
            return data

    with create_client(routes=[Gateway(handler=ItemsUUIDController)], debug=True) as client:
        headers = {"Content-Type": "application/json"}
        payload = {"id": uuid4().hex, "name": "Test Item"}

        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 201
        assert UUID(response.json()["id"]).hex == payload["id"]
        assert response.json()["name"] == payload["name"]

        response = client.post("/items", json=payload, headers=headers)
        assert response.status_code == 201
        assert UUID(response.json()["id"]).hex == payload["id"]
        assert response.json()["name"] == payload["name"]

        response = client.put(f"/items/{payload['id']}", json=payload, headers=headers)
        assert response.status_code == 200
        assert UUID(response.json()["id"]).hex == payload["id"]
        assert response.json()["name"] == payload["name"]

        response = client.patch(f"/items/{payload['id']}", json=payload, headers=headers)
        assert response.status_code == 200
        assert UUID(response.json()["id"]).hex == payload["id"]
        assert response.json()["name"] == payload["name"]

        response = client.delete(f"/items/{payload['id']}", headers=headers)
        assert response.status_code == 204

        item_id = payload["id"]
        response = client.get(f"/items/{item_id}", headers=headers)
        assert response.status_code == 200
        assert UUID(response.json()["id"]).hex == item_id