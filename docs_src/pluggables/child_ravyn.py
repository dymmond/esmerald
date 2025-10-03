from typing import Optional

from loguru import logger

from ravyn import ChildRavyn, Ravyn, Extension, Gateway, JSONResponse, Pluggable, get
from ravyn.types import DictAny


@get("/home")
async def home() -> JSONResponse:
    return JSONResponse({"detail": "Welcome"})


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


app = Ravyn(routes=[], extensions={"child-ravyn": Pluggable(ChildRavynPluggable)})
