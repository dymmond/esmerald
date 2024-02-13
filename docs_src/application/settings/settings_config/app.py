from esmerald import Esmerald, Gateway, JSONResponse, Request, get

from .configs.app_settings import InstanceSettings


@get()
async def home(request: Request) -> JSONResponse: ...


app = Esmerald(routes=[Gateway(handler=home)], settings_config=InstanceSettings)
