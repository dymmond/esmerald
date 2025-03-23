from typing import Any

from esmerald import Factory, Gateway, JSONResponse, get
from esmerald.protocols.asyncdao import AsyncDAOProtocol
from esmerald.testclient import create_client


class AnotherFakeDAO(AsyncDAOProtocol):
    model = "Awesome"

    def __init__(self, value: str = "awesome_conn", **kwargs: Any):
        self.value = value
        self.kwargs = kwargs

    async def get_all(self, **kwargs: Any):
        return ["awesome_data"]

    async def get_kwargs(self):
        return self.kwargs


@get(
    "/test",
    dependencies={
        "dao": Factory(AnotherFakeDAO, "awesome_conn", db_session="session", cache="cache")
    },
)
async def test_view(dao: AnotherFakeDAO) -> JSONResponse:
    res = await dao.get_kwargs()
    return JSONResponse(res)


def test_kwargs_in_factory():
    """Ensure Factory correctly passes keyword arguments."""

    with create_client(routes=[Gateway(handler=test_view)]) as client:
        response = client.get("/test")
        assert response.status_code == 200
        assert response.json() == {"db_session": "session", "cache": "cache"}
