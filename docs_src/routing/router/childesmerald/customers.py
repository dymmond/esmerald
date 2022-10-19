from pydantic import BaseModel

from esmerald import ChildEsmerald, Gateway, UJSONResponse, get, post


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


router = ChildEsmerald(
    routes=[
        Gateway("/", handler=get_customer),
        Gateway("/create", handler=create),
    ],
    include_in_schema=...,
    response_class=...,
    response_headers=...,
    response_cookies=...,
)
