from functools import partial
from typing import Any

import pytest

from esmerald.injector import Factory, Inject
from esmerald.typing import Void


class Test:
    __test__ = False

    val = 31

    def __init__(self) -> None:
        self.val = 13

    @classmethod
    async def async_class(cls) -> int:
        return cls.val

    class InsideTest:
        val = 56

        @classmethod
        async def async_class(cls) -> int:
            return cls.val

        class NestedInsideTest:
            val = 92

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

async_factory = Factory(async_fn, "why-three-and-one")
sync_factory = Factory(sync_fn, "why-three-and-one")
test_factory = Factory(Test)


@pytest.mark.parametrize(
    "_callable,exp",
    [
        (async_fn, "three-one"),
        (Factory(async_fn), "three-one"),
        (Factory("tests.test_inject.async_fn"), "three-one"),
    ],
)
@pytest.mark.asyncio()
async def test_Inject_default(_callable, exp) -> None:
    Injectr = Inject(dependency=_callable)
    value = await Injectr()
    assert value == exp


@pytest.mark.parametrize(
    "_callable,exp",
    [
        (async_fn, "three-one"),
        (Factory(async_fn), "three-one"),
        (Factory("tests.test_inject.async_fn"), "three-one"),
    ],
)
@pytest.mark.asyncio()
async def test_Inject_cached(_callable, exp) -> None:
    Injectr = Inject(dependency=_callable, use_cache=True)
    assert Injectr.value is Void
    value = await Injectr()
    assert value == exp
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


def test_Injectr_equality_check_Factory() -> None:
    first_Injectr = Inject(dependency=Factory(sync_fn))
    second_Injectr = Inject(dependency=Factory(sync_fn))
    # The Factory is intended to return different objects, that's why 2 same Factory Injects are different
    assert first_Injectr != second_Injectr
    third_Injectr = Inject(dependency=Factory(sync_fn), use_cache=True)
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
        (async_factory, "why-three-and-one"),
        (sync_factory, "why-three-and-one"),
        (Factory(Test.async_class), 31),
        (Factory(Test.sync_class), 31),
        (Factory(Test.async_static), "one-three"),
        (Factory(Test.sync_static), "one-three"),
        (Factory(Test().async_instance), 13),
        (Factory(Test().sync_instance), 13),
        (Factory("tests.test_inject.async_fn"), "three-one"),
        (Factory("tests.test_inject.Test.async_class"), 31),
        (Factory("tests.test_inject.Test.sync_class"), 31),
        (Factory("tests.test_inject.Test.async_static"), "one-three"),
        (Factory("tests.test_inject.Test.sync_static"), "one-three"),
        (Factory("tests.test_inject.Test.InsideTest.async_class"), 56),
        (Factory("tests.test_inject.Test.InsideTest.NestedInsideTest.async_class"), 92),
    ],
)
@pytest.mark.asyncio()
async def test_Inject_for_callable(fn: Any, exp: Any) -> None:
    assert await Inject(fn)() == exp


@pytest.mark.asyncio()
async def test_if_DAO_is_injectable(get_fake_dao) -> None:
    """
    Current:
    dependencies={
            "fake_dao": Inject(lambda: FakeDAO()),
        },

    dependencies={
            "fake_dao": Inject(lambda: FakeDAO(conn="nice_conn")),
        },

    Alternative:
    dependencies={
            "fake_dao": Inject(Factory(FakeDAO)),
        },
    dependencies={
            "fake_dao": Inject(Factory(FakeDAO, "nice_conn")),
        },
    """
    injectable1 = Inject(Factory(get_fake_dao))
    obj = await injectable1()
    assert await obj.get_all() == ["awesome_data"]
    assert obj.model == "Awesome"
    assert obj.conn == "awesome_conn"

    injectable2 = Inject(Factory(get_fake_dao, "nice_conn"))
    obj = await injectable2()
    assert await obj.get_all() == ["awesome_data"]
    assert obj.model == "Awesome"
    assert obj.conn == "nice_conn"

    assert injectable1 != injectable2
