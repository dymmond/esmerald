import anyio
import pytest

from esmerald.param_functions import Requires
from esmerald.utils.dependencies import async_resolve_dependencies, resolve_dependencies


def get_user():
    return {"id": 1, "name": "Alice"}


def get_current_user(user=Requires(get_user)):
    return user


async def get_async_user():
    await anyio.sleep(0.1)
    return {"id": 2, "name": "Bob"}


async def async_endpoint(current_user=Requires(get_async_user)):
    return {"message": "Hello", "user": current_user}


def endpoint(current_user=Requires(get_current_user)):
    return {"message": "Hello", "user": current_user}


@pytest.mark.asyncio
async def test_required_dependency_async():
    async_result = await async_resolve_dependencies(async_endpoint)

    assert async_result == {"message": "Hello", "user": {"id": 2, "name": "Bob"}}


def test_required_dependency():
    result = resolve_dependencies(endpoint)
    assert result == {"message": "Hello", "user": {"id": 1, "name": "Alice"}}
