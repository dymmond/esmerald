from typing import Any, Dict

from esmerald import Inject, Injects, Esmerald, get, Gateway
from esmerald.security.http import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()


@get("/items", dependencies={"credentials": Inject(security)}, security=[security])
async def get_items(credentials: HTTPAuthorizationCredentials = Injects()) -> Dict[str, Any]:
    return {"scheme": credentials.scheme, "credentials": credentials.credentials}


app = Esmerald(
    routes=[
        Gateway(handler=get_items),
    ]
)
