from pydantic import BaseModel

from esmerald import Esmerald, Gateway, Response, get
from esmerald.core.datastructures import Cookie


class Item(BaseModel):
    id: int
    sku: str


@get(path="/me")
async def home() -> Response[Item]:
    return Response(
        Item(id=1, sku="sku1238"),
        headers={"SKY-HEADER": "sku-xyz"},
        cookies=[Cookie(key="sku", value="a-value")],
    )


app = Esmerald(routes=[Gateway(handler=home)])
