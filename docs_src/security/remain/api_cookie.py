from typing import Any, Dict

from esmerald import Inject, Injects, Esmerald, get, Gateway
from esmerald.security.api_key import APIKeyInCookie

security = APIKeyInCookie(name="session")


@get("/items", dependencies={"session": Inject(security)}, security=[security])
async def get_items(session: str = Injects()) -> Dict[str, Any]:
    return {"session": session}


app = Esmerald(
    routes=[
        Gateway(handler=get_items),
    ]
)
