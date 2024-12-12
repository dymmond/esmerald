from typing import Any, Dict

from esmerald import Inject, Injects, Esmerald, get, Gateway
from esmerald.security.api_key import APIKeyInQuery

security = APIKeyInQuery(name="api_key")


@get("/items", dependencies={"api_key": Inject(security)}, security=[security])
async def get_items(api_key: str = Injects()) -> Dict[str, Any]:
    return {"api_key": api_key}


app = Esmerald(
    routes=[
        Gateway(handler=get_items),
    ]
)
