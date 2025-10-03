from ravyn import Ravyn, Gateway, get
from ravyn.utils.decorators import cache


@get("/expensive/{value}")
@cache(ttl=10)  # Cache for 10 seconds
async def expensive_operation(value: int) -> dict:
    return {"result": value * 2}


app = Ravyn(routes=[Gateway(handler=expensive_operation)])
