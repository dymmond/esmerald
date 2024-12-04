from typing import AsyncGenerator, Generator

import pytest

from esmerald import Esmerald, Gateway, get
from esmerald.param_functions import Requires
from esmerald.testclient import EsmeraldTestClient


class CallableDependency:  # pragma: no cover
    def __call__(self, value: str) -> str:
        return value


class CallableGenDependency:  # pragma: no cover
    def __call__(self, value: str) -> Generator[str, None, None]:
        yield value


class AsyncCallableDependency:  # pragma: no cover
    async def __call__(self, value: str) -> str:
        return value


class AsyncCallableGenDependency:  # pragma: no cover
    async def __call__(self, value: str) -> AsyncGenerator[str, None]:
        yield value


class MethodsDependency:  # pragma: no cover
    def synchronous(self, value: str) -> str:
        return value

    async def asynchronous(self, value: str) -> str:
        return value

    def synchronous_gen(self, value: str) -> Generator[str, None, None]:
        yield value

    async def asynchronous_gen(self, value: str) -> AsyncGenerator[str, None]:
        yield value


callable_dependency = CallableDependency()
callable_gen_dependency = CallableGenDependency()
async_callable_dependency = AsyncCallableDependency()
async_callable_gen_dependency = AsyncCallableGenDependency()
methods_dependency = MethodsDependency()


@get("/callable-dependency")
async def get_callable_dependency(value: str = Requires(callable_dependency)) -> str:
    return value


@get("/callable-gen-dependency")
async def get_callable_gen_dependency(value: str = Requires(callable_gen_dependency)) -> str:
    return value


@get("/async-callable-dependency")
async def get_async_callable_dependency(
    value: str = Requires(async_callable_dependency),
) -> str:
    return value


@get("/async-callable-gen-dependency")
async def get_async_callable_gen_dependency(
    value: str = Requires(async_callable_gen_dependency),
) -> str:
    return value


@get("/synchronous-method-dependency")
async def get_synchronous_method_dependency(
    value: str = Requires(methods_dependency.synchronous),
) -> str:
    return value


@get("/synchronous-method-gen-dependency")
async def get_synchronous_method_gen_dependency(
    value: str = Requires(methods_dependency.synchronous_gen),
) -> str:
    return value


@get("/asynchronous-method-dependency")
async def get_asynchronous_method_dependency(
    value: str = Requires(methods_dependency.asynchronous),
) -> str:
    return value


@get("/asynchronous-method-gen-dependency")
async def get_asynchronous_method_gen_dependency(
    value: str = Requires(methods_dependency.asynchronous_gen),
) -> str:
    return value


app = Esmerald(
    routes=[
        Gateway(handler=get_callable_dependency),
        Gateway(handler=get_callable_gen_dependency),
        Gateway(handler=get_async_callable_dependency),
        Gateway(handler=get_async_callable_gen_dependency),
        Gateway(handler=get_synchronous_method_dependency),
        Gateway(handler=get_synchronous_method_gen_dependency),
        Gateway(handler=get_asynchronous_method_dependency),
        Gateway(handler=get_asynchronous_method_gen_dependency),
    ]
)


client = EsmeraldTestClient(app)


@pytest.mark.parametrize(
    "route,value",
    [
        ("/callable-dependency", "callable-dependency"),
        ("/callable-gen-dependency", "callable-gen-dependency"),
        ("/async-callable-dependency", "async-callable-dependency"),
        ("/async-callable-gen-dependency", "async-callable-gen-dependency"),
        ("/synchronous-method-dependency", "synchronous-method-dependency"),
        ("/synchronous-method-gen-dependency", "synchronous-method-gen-dependency"),
        ("/asynchronous-method-dependency", "asynchronous-method-dependency"),
        ("/asynchronous-method-gen-dependency", "asynchronous-method-gen-dependency"),
    ],
)
def test_class_dependency(route, value):
    response = client.get(route, params={"value": value})
    assert response.status_code == 200, response.text
    assert response.json() == value
