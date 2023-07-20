from pydantic import BaseModel, ValidationError, field_validator

from esmerald import JSON, Gateway, post, put
from esmerald.exception_handlers import pydantic_validation_error_handler, value_error_handler
from esmerald.testclient import create_client


class DataIn(BaseModel):
    """
    Model example with DataIn for custom cases
    and testing purposes.
    """

    name: str
    email: str

    @field_validator("name")
    def validate_name(cls, name: str) -> str:
        raise ValueError(f"The name: {name} was successfully passed")


@post("/create")
async def create() -> JSON:
    DataIn()


@post("/raise-error")
async def raised() -> JSON:
    raise ValueError("Error raised here.")


@put("/update")
async def update() -> JSON:
    DataIn(name="Esmerald", email="test@esmerald.dev")


def test_pydantic_validation_error_handler_return_422(test_client_factory):
    with create_client(
        routes=[Gateway(handler=create)],
    ) as client:
        response = client.post("/create")
        assert response.status_code == 422


def test_pydantic_validation_error_handler(test_client_factory):
    with create_client(
        routes=[Gateway(handler=create)],
        exception_handlers={ValidationError: pydantic_validation_error_handler},
    ) as client:
        response = client.post("/create")
        assert response.status_code == 422

        details = response.json()["detail"]

        assert len(details) == 2

        for detail in details:
            assert detail["type"] == "missing"
            assert detail["msg"] == "Field required"

        locs = [detail["loc"][0] for detail in details]

        assert "name" in locs
        assert "email" in locs


def test_value_error_handler_return_500_on_function(test_client_factory):
    with create_client(
        routes=[Gateway(handler=raised)],
    ) as client:
        response = client.post("/raise-error")

        assert response.status_code == 500


def test_value_error_handler_simple(test_client_factory):
    with create_client(
        routes=[Gateway(handler=raised)],
        exception_handlers={ValueError: value_error_handler},
    ) as client:
        response = client.post("/raise-error")
        assert response.status_code == 400

        assert response.json()["detail"] == "Error raised here."
