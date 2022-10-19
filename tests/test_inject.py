from functools import partial
from typing import Any

import pytest
from esmerald.injector import Inject
from esmerald.typing import Void


class Test:
    __test__ = False

    val = 31

    def __init__(self) -> None:
        self.val = 13

    @classmethod
    async def async_class(cls) -> int:
        return cls.val

    @classmethod
    def sync_class(cls) -> int:
        return cls.val

    @staticmethod
    async def async_static() -> str:
        return "one-three"

    @staticmethod
    def sync_static() -> str:
        return "one-three"

    async def async_instance(self) -> int:
        return self.val

    def sync_instance(self) -> int:
        return self.val


async def async_fn(val: str = "three-one") -> str:
    return val


def sync_fn(val: str = "three-one") -> str:
    return val


async_partial = partial(async_fn, "why-three-and-one")
sync_partial = partial(sync_fn, "why-three-and-one")


@pytest.mark.asyncio()
async def test_Inject_default() -> None:
    Injectr = Inject(dependency=async_fn)
    value = await Injectr()
    assert value == "three-one"


@pytest.mark.asyncio()
async def test_Inject_cached() -> None:
    Injectr = Inject(dependency=async_fn, use_cache=True)
    assert Injectr.value is Void
    value = await Injectr()
    assert value == "three-one"
    assert Injectr.value == value
    second_value = await Injectr()
    assert value == second_value
    third_value = await Injectr()
    assert value == third_value


def test_Injectr_equality_check() -> None:
    first_Injectr = Inject(dependency=sync_fn)
    second_Injectr = Inject(dependency=sync_fn)
    assert first_Injectr == second_Injectr
    third_Injectr = Inject(dependency=sync_fn, use_cache=True)
    assert first_Injectr != third_Injectr
    second_Injectr.value = True
    assert first_Injectr != second_Injectr


@pytest.mark.parametrize(
    "fn, exp",
    [
        (Test.async_class, 31),
        (Test.sync_class, 31),
        (Test.async_static, "one-three"),
        (Test.sync_static, "one-three"),
        (Test().async_instance, 13),
        (Test().sync_instance, 13),
        (async_fn, "three-one"),
        (sync_fn, "three-one"),
        (async_partial, "why-three-and-one"),
        (sync_partial, "why-three-and-one"),
    ],
)
@pytest.mark.asyncio()
async def test_Inject_for_callable(fn: Any, exp: Any) -> None:
    assert await Inject(fn)() == exp
