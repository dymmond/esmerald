from dataclasses import dataclass

import pytest
from pydantic import BaseModel

from esmerald import get
from esmerald.openapi.datastructures import OpenAPIResponse


class Error(BaseModel):
    status: int
    detail: str


@dataclass
class DummyErrorDataclass:
    status: int
    detail: str


class DummyError:
    ...


def test_openapi_response_value_error_for_type(test_client_factory):
    with pytest.raises(ValueError):

        @get(
            "/item/{id}",
            responses={422: OpenAPIResponse(model={"hello", Error}, description="Error")},
        )
        async def read_item(id: str) -> None:
            ...


@pytest.mark.parametrize(
    "model",
    [DummyErrorDataclass, DummyError],
)
def test_openapi_response_value_for_class(test_client_factory, model):
    with pytest.raises(ValueError):

        @get(
            "/item/{id}",
            responses={422: OpenAPIResponse(model=model, description="Error")},
        )
        async def read_item(id: str) -> None:
            ...


@pytest.mark.parametrize(
    "model",
    [DummyErrorDataclass, DummyError],
)
def test_openapi_response_value_for_class_as_list(test_client_factory, model):
    with pytest.raises(ValueError):

        @get(
            "/item/{id}",
            responses={422: OpenAPIResponse(model=[model], description="Error")},
        )
        async def read_item(id: str) -> None:
            ...
