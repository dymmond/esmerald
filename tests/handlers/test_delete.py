from esmerald.routing.gateways import Gateway
from esmerald.routing.handlers import delete
from esmerald.testclient import create_client


def test_handler_return_none_and_204_status_response_empty() -> None:
    @delete(path="/")
    async def test() -> None:  # type: ignore[valid-type]
        return None

    with create_client(routes=[Gateway(path="/", handler=test)]) as client:
        response = client.delete("/")
        assert not response.content
