from typing import Any, Dict

from esmerald import Inject, Injects, Esmerald, get, Gateway
from esmerald.security.api_key import APIKeyInHeader

security = APIKeyInHeader(name="X_API_KEY")


@get("/items", dependencies={"key": Inject(security)}, security=[security])
async def get_items(key: str = Injects()) -> Dict[str, Any]:
    return {"key": key}


app = Esmerald(
    routes=[
        Gateway(handler=get_items),
    ]
)
