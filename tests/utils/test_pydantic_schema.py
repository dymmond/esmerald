from typing import Any

import pytest

from esmerald.params import Param
from esmerald.utils.pydantic.schema import is_any_type, is_field_optional


def test_is_any_type():
    field = Param(annotation=Any)

    assert is_any_type(field)


@pytest.mark.parametrize("allow_none,return_type", [(True, False), (False, False)])
def test_is_field_optional(allow_none, return_type):
    field = Param(allow_none=allow_none)

    assert is_field_optional(field) == return_type
