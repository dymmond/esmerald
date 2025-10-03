from ravyn import Ravyn, Gateway, JSONResponse, Request, get

from .configs.app_settings import InstanceSettings


@get()
async def home(request: Request) -> JSONResponse: ...


app = Ravyn(routes=[Gateway(handler=home)], settings_module=InstanceSettings)
