from ravyn import Ravyn, Gateway, get
from ravyn.conf import settings


@get()
async def app_name() -> dict:
    return {"app_name": settings.app_name}


app = Ravyn(routes=[Gateway(handler=app_name)])
