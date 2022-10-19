from pydantic import BaseModel

from esmerald import Gateway, Router, UJSONResponse, get, post


class Address(BaseModel):
    address_line: str
    street: str
    post_code: str


class Customer(BaseModel):
    name: str
    email: str
    address: Address


@post("/")
def create(data: Customer) -> UJSONResponse:
    return UJSONResponse({"created": True})


@get("/{customer_id:int}")
async def get_customer(customer_id: int) -> UJSONResponse:
    return UJSONResponse({"created": True})


router = Router(
    path="/customers",
    routes=[
        Gateway("/", handler=get_customer),
        Gateway("/create", handler=create),
    ],
)
