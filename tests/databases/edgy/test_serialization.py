import random
import string
from typing import AsyncGenerator
from uuid import uuid4

import edgy
import pytest
from httpx import AsyncClient

from esmerald import Esmerald, Gateway, post
from esmerald.conf import settings

database, models = settings.edgy_registry
pytestmark = pytest.mark.anyio


def get_random_string(length=10):
    letters = string.ascii_lowercase
    result_str = "".join(random.choice(letters) for i in range(length))
    return result_str


class TestUser(edgy.Model):
    """
    Inherits from the abstract user and adds the registry
    from esmerald settings.
    """

    name = edgy.CharField(max_length=255, null=False)
    user_id = edgy.UUIDField(default=uuid4)
    created_at = edgy.DateTimeField(auto_now=True)
    updated_at = edgy.DateTimeField(auto_now_add=True)

    class Meta:
        registry = models


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
    with database.force_rollback():
        async with database:
            yield


@pytest.fixture()
def app() -> Esmerald:
    app = Esmerald(routes=[Gateway(handler=user)])
    return app


@pytest.fixture()
async def async_client(app) -> AsyncGenerator:
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@post("/create")
async def user() -> TestUser:
    user = await TestUser.query.create(name="Esmerald")
    return user


async def test_can_create_user_serialized(test_client_factory, async_client):
    response = await async_client.post("/create")

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Esmerald"
    assert data["created_at"] is not None
    assert data["updated_at"] is not None
    assert data["user_id"] is not None
