from json import loads

import pytest

from ravyn.core.transformers.signature import SignatureFactory
from ravyn.routing.handlers import post, route
from ravyn.utils.enums import HttpMethod
from tests.models import Individual, IndividualFactory


@pytest.mark.asyncio()
async def test_to_response_async_await() -> None:
    @route(methods=[HttpMethod.POST], path="/person")
    async def test_function(payload: Individual) -> Individual:
        assert isinstance(payload, Individual)
        return payload

    person_instance = IndividualFactory.build()
    test_function.signature_model = SignatureFactory(
        test_function.fn,
        set(),  # type:ignore[arg-type]
    ).create_signature()

    response = await test_function.to_response(
        data=test_function.fn(payload=person_instance),
        app=None,  # type: ignore
    )
    assert loads(response.body) == person_instance.model_dump()


@pytest.mark.asyncio()
async def test_to_response_async_await_with_post_handler() -> None:
    @post(path="/person")
    async def test_function(payload: Individual) -> Individual:
        assert isinstance(payload, Individual)
        return payload

    person_instance = IndividualFactory.build()
    test_function.signature_model = SignatureFactory(
        test_function.fn,
        set(),  # type:ignore[arg-type]
    ).create_signature()

    response = await test_function.to_response(
        data=test_function.fn(payload=person_instance),
        app=None,  # type: ignore
    )
    assert loads(response.body) == person_instance.model_dump()
