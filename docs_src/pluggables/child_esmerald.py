from typing import Optional

from loguru import logger

from esmerald import ChildEsmerald, Esmerald, Extension, Gateway, JSONResponse, Pluggable, get
from esmerald.types import DictAny


@get("/home")
async def home() -> JSONResponse:
    return JSONResponse({"detail": "Welcome"})


class ChildEsmeraldPluggable(Extension):
    def __init__(self, app: Optional["Esmerald"] = None, **kwargs: "DictAny"):
        super().__init__(app, **kwargs)
        self.app = app
        self.kwargs = kwargs

    def extend(self, **kwargs: "DictAny") -> None:
        """
        Add a child Esmerald into the main application.
        """
        # Do something here like print a log or whatever you need
        logger.info("Adding the ChildEsmerald via pluggable...")

        child = ChildEsmerald(routes=[Gateway(handler=home, name="child-esmerald-home")])
        self.app.add_child_esmerald(path="/pluggable", child=child)

        logger.success("Added the ChildEsmerald via pluggable.")


app = Esmerald(routes=[], pluggables={"child-esmerald": Pluggable(ChildEsmeraldPluggable)})
