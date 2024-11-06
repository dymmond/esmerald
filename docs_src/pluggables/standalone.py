from typing import Optional

from loguru import logger

from esmerald import Esmerald, Gateway, JSONResponse, Request, get
from esmerald.types import DictAny


class Standalone:
    def __init__(self, app: Optional["Esmerald"] = None, **kwargs: "DictAny"):
        self.app = app
        self.kwargs = kwargs

    def extend(self, **kwargs: "DictAny") -> None:
        """
        Function that should always be implemented when extending
        the Extension class or a `NotImplementedError` is raised.
        """
        # Do something here like print a log or whatever you need
        logger.success("Started the extension manually")

        # Add the extension to the pluggables of Esmerald
        # And make it accessible
        self.app.add_pluggable("standalone", self)


@get("/home")
async def home(request: Request) -> JSONResponse:
    """
    Returns a list of pluggables of the system.

    "pluggables": ["standalone"]
    """
    pluggables = list(request.app.pluggables)

    return JSONResponse({"pluggables": pluggables})


app = Esmerald(routes=[Gateway(handler=home)])

extension = Standalone(app=app)
extension.extend()
