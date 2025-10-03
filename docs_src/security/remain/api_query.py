from typing import Any, Dict

from ravyn import Inject, Injects, Ravyn, get, Gateway
from ravyn.security.api_key import APIKeyInQuery

security = APIKeyInQuery(name="api_key")


@get("/items", dependencies={"api_key": Inject(security)}, security=[security])
async def get_items(api_key: str = Injects()) -> Dict[str, Any]:
    return {"api_key": api_key}


app = Ravyn(
    routes=[
        Gateway(handler=get_items),
    ]
)
