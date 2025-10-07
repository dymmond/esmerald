from pydantic import BaseModel

from ravyn import (
    Controller,
    JSONResponse,
    Request,
    Response,
    WebSocket,
    get,
    post,
    put,
    status,
    websocket,
)


class Product(BaseModel):
    name: str
    sku: str
    price: float


@put("/product/{product_id}")
def update_product(product_id: int, data: Product) -> dict:
    return {"product_id": product_id, "product_name": data.name}


@get(status_code=status.HTTP_200_OK)
async def home() -> JSONResponse:
    return JSONResponse({"detail": "Hello world"})


@get()
async def another(request: Request) -> dict:
    return {"detail": "Another world!"}


@websocket(path="/{path_param:str}")
async def world_socket(socket: WebSocket) -> None:
    await socket.accept()
    msg = await socket.receive_json()
    assert msg
    assert socket
    await socket.close()


class World(Controller):
    @get(path="/{url}")
    async def home(self, request: Request, url: str) -> Response:
        return Response(f"URL: {url}")

    @post(path="/{url}", status_code=status.HTTP_201_CREATED)
    async def mars(self, request: Request, url: str) -> JSONResponse: ...

    @websocket(path="/{path_param:str}")
    async def pluto(self, socket: WebSocket) -> None:
        await socket.accept()
        msg = await socket.receive_json()
        assert msg
        assert socket
        await socket.close()
