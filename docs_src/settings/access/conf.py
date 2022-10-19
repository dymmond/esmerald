from esmerald import Esmerald, Gateway, get
from esmerald.conf import settings


@get()
async def app_name() -> dict:
    return {"app_name": settings.app_name}


app = Esmerald(routes=[Gateway(handler=app_name)])
