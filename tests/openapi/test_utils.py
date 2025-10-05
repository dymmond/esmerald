import pytest

from ravyn import status
from ravyn.openapi.utils import is_status_code_allowed

status_codes_allowed = [
    getattr(status, value)
    for value in dir(status)
    if value.startswith("HTTP")
    and not (getattr(status, value) < 200 or getattr(status, value) in {204, 304})
]

status_codes_not_allowed = [
    getattr(status, value)
    for value in dir(status)
    if value.startswith("HTTP")
    and (getattr(status, value) < 200 or getattr(status, value) in {204, 304})
]


def test_is_status_code_allowed():
    assert is_status_code_allowed(None)


@pytest.mark.parametrize(
    "code",
    [
        "default",
        "1XX",
        "2XX",
        "3XX",
        "4XX",
        "5XX",
    ],
)
def test_is_status_code_allowed_str(code):
    assert is_status_code_allowed(code)


@pytest.mark.parametrize("code", status_codes_allowed)
def test_test_is_status_code_allowed_allowed_code(code):
    assert is_status_code_allowed(str(code))


@pytest.mark.parametrize("code", status_codes_not_allowed)
def test_test_is_status_code_not_allowed(code):
    assert not is_status_code_allowed(str(code))
