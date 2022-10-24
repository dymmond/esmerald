import re
from typing import TYPE_CHECKING

from esmerald.exceptions import ImproperlyConfigured
from openapi_schemas_pydantic.utils.constants import PYDANTIC_FIELD_SHAPE_MAP

if TYPE_CHECKING:
    from openapi_schemas_pydantic.utils.enums import OpenAPIType
    from pydantic.fields import ModelField

CAPITAL_LETTERS_PATTERN = re.compile(r"(?=[A-Z])")


def pascal_case_to_text(string: str) -> str:
    """Given a 'PascalCased' string, return its split form- 'Pascal Cased'."""
    return " ".join(re.split(CAPITAL_LETTERS_PATTERN, string)).strip()


def get_openapi_type_for_complex_type(field: "ModelField") -> "OpenAPIType":
    """We are dealing with complex types in this case.

    The problem here is that the Python typing system is too crude to
    define OpenAPI objects properly.
    """
    try:
        return PYDANTIC_FIELD_SHAPE_MAP[field.shape]
    except KeyError as e:
        raise ImproperlyConfigured(
            f"Parameter '{field.name}' with type '{field.outer_type_}' could not be mapped to an Open API type. "
            f"This can occur if a user-defined generic type is resolved as a parameter. If '{field.name}' should "
            "not be documented as a parameter, annotate it using the `Dependency` function, e.g., "
            f"`{field.name}: ... = Dependency(...)`."
        ) from e
