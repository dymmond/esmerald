from typing import Any, Dict

from ravyn import Inject, Injects, Ravyn, get, Gateway
from ravyn.security.api_key import APIKeyInCookie

security = APIKeyInCookie(name="session")


@get("/items", dependencies={"session": Inject(security)}, security=[security])
async def get_items(session: str = Injects()) -> Dict[str, Any]:
    return {"session": session}


app = Ravyn(
    routes=[
        Gateway(handler=get_items),
    ]
)
