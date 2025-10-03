from typing import Any, Dict

from ravyn import Inject, Injects, Ravyn, get, Gateway
from ravyn.security.http import HTTPDigest, HTTPAuthorizationCredentials

security = HTTPDigest()


@get("/items", dependencies={"credentials": Inject(security)}, security=[security])
async def get_items(credentials: HTTPAuthorizationCredentials = Injects()) -> Dict[str, Any]:
    return {"scheme": credentials.scheme, "credentials": credentials.credentials}


app = Ravyn(
    routes=[
        Gateway(handler=get_items),
    ]
)
