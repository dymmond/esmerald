from typing import Optional

from loguru import logger

from ravyn import Ravyn, Extension, Gateway, JSONResponse, Request, get
from ravyn.types import DictAny


class MyExtension(Extension):
    def __init__(self, app: Optional["Ravyn"] = None, **kwargs: "DictAny"):
        super().__init__(app, **kwargs)
        self.app = app
        self.kwargs = kwargs

    def extend(self, **kwargs: "DictAny") -> None:
        """
        Function that should always be implemented when extending
        the Extension class or a `NotImplementedError` is raised.
        """
        # Do something here like print a log or whatever you need
        logger.success("Started the extension manually")

        # Add the extension to the extensions of Ravyn
        # And make it accessible
        self.app.add_extension("my-extension", self)


@get("/home")
async def home(request: Request) -> JSONResponse:
    """
    Returns a list of extensions of the system.

    "extensions": ["my-extension"]
    """
    extensions = list(request.app.extensions)

    return JSONResponse({"extensions": extensions})


app = Ravyn(routes=[Gateway(handler=home)])

extension = MyExtension(app=app)
extension.extend()
