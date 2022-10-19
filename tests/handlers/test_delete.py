from typing import Any, NoReturn

import pytest

from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import delete
from esmerald.testclient import create_client


@pytest.mark.parametrize("return_annotation", (None, NoReturn))
def test_handler_return_none_and_204_status_response_empty(
    return_annotation: Any,
) -> None:
    @delete(path="/")
    async def test() -> return_annotation:  # type: ignore[valid-type]
        return None

    route = Gateway(path="/", handler=test)

    with create_client(routes=[route]) as client:
        response = client.delete("/")
        assert not response.content
