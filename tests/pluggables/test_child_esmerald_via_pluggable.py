from typing import Optional

from loguru import logger

from ravyn import (
    ChildRavyn,
    Extension,
    Gateway,
    JSONResponse,
    Pluggable,
    Ravyn,
    Request,
    get,
)
from ravyn.testclient import EsmeraldTestClient
from ravyn.types import DictAny


@get("/")
async def home(request: Request) -> JSONResponse:
    """
    Returns a list of extensions of the system.

    "extensions": ["standalone"]
    """
    extensions = list(request.app.extensions)

    return JSONResponse({"extensions": extensions})


class ChildRavynPluggable(Extension):
    def __init__(self, app: Optional["Ravyn"] = None, **kwargs: "DictAny"):
        super().__init__(app, **kwargs)
        self.app = app
        self.kwargs = kwargs

    def extend(self, **kwargs: "DictAny") -> None:
        """
        Add a child Ravyn into the main application.
        """
        # Do something here like print a log or whatever you need
        logger.info("Adding the ChildRavyn via pluggable...")

        child = ChildRavyn(routes=[Gateway(handler=home, name="child-ravyn-home")])
        self.app.add_child_esmerald(path="/pluggable", child=child)

        logger.success("Added the ChildRavyn via pluggable.")


def test_can_add_child_esmerald_via_pluggable():
    app = Ravyn(routes=[], extensions={"child-ravyn": Pluggable(ChildRavynPluggable)})

    client = EsmeraldTestClient(app=app)

    response = client.get("/pluggable")

    assert response.status_code == 200
