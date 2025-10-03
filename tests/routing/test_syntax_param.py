from ravyn import Gateway, JSONResponse, get
from ravyn.testclient import create_client


@get("/users/<user_id>")
async def user(user_id: str) -> JSONResponse:
    return JSONResponse({"user_id": user_id})


@get("/products/<product_id:int>")
async def product(product_id: int) -> JSONResponse:
    return JSONResponse({"product_id": product_id})


def test_syntax():
    with create_client(routes=[Gateway(handler=user), Gateway(handler=product)]) as client:
        response = client.get("/users/1")
        assert response.json() == {"user_id": "1"}

        response = client.get("/products/1")
        assert response.json() == {"product_id": 1}
