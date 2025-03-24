from esmerald import Esmerald, Gateway, get
from esmerald.utils.decorators import cache


@get("/expensive/{value}")
@cache(ttl=10)  # Cache for 10 seconds
async def expensive_operation(value: int) -> dict:
    return {"result": value * 2}


app = Esmerald(routes=[Gateway(handler=expensive_operation)])
