from typing import Any, Dict

from esmerald import Inject, Injects, Esmerald, get, Gateway
from esmerald.security.open_id import OpenIdConnect

security = OpenIdConnect(openIdConnectUrl="/openid", description="OpenIdConnect security scheme")


@get("/items", dependencies={"auth": Inject(security)}, security=[security])
async def get_items(auth: str = Injects()) -> Dict[str, Any]:
    return {"auth": auth}


app = Esmerald(
    routes=[
        Gateway(handler=get_items),
    ]
)
