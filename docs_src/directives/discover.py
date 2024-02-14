from pydantic import BaseModel

from esmerald import Esmerald, Gateway, JSONResponse, Request, get, route


class Item(BaseModel):
    sku: int
    name: str


@get("/{name}")
async def show_name(name: str) -> JSONResponse:
    return JSONResponse({"name": name})


@route("/create", methods=["POST", "PUT"])
async def create_or_update_item(data: Item, request: Request, name: str) -> JSONResponse:
    # Does something with PUT or POST
    ...


def get_application():
    app = Esmerald(
        routes=[
            Gateway(handler=show_name),
            Gateway(path="/item", handler=create_or_update_item),
        ],
    )

    return app


app = get_application()
