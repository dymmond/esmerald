import pytest

from esmerald.param_functions import Requires
from esmerald.utils.dependencies import RequiresDependency, get_requires_dependency


def function_one():
    return "function_one"


def function_two(name=Requires(function_one)):
    return name


def function_three(name=Requires(function_two)):
    return name


@pytest.mark.asyncio
async def test_required_dependency():

    injector = RequiresDependency()
    requires = await get_requires_dependency(injector, function_three)

    assert requires.dependency() == "function_one"
  
