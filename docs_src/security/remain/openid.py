from typing import Any, Dict

from ravyn import Inject, Injects, Ravyn, get, Gateway
from ravyn.security.open_id import OpenIdConnect

security = OpenIdConnect(openIdConnectUrl="/openid", description="OpenIdConnect security scheme")


@get("/items", dependencies={"auth": Inject(security)}, security=[security])
async def get_items(auth: str = Injects()) -> Dict[str, Any]:
    return {"auth": auth}


app = Ravyn(
    routes=[
        Gateway(handler=get_items),
    ]
)
